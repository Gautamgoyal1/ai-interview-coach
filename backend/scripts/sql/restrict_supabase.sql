-- Operator-only, dedicated staging project, AFTER alembic upgrade head.
-- Run in one psql session with ON_ERROR_STOP=1. No credentials in this file.
-- SET prepmate.reviewed_dedicated_project = 'yes'; is required separately.
BEGIN;
DO $$
DECLARE
    target text;
    api_role text;
    sequence_name text;
    targets text[] := ARRAY['users','resumes','resume_analyses','interview_sessions',
        'interview_turns','interview_reports','practice_sessions','practice_questions',
        'practice_attempts','chunks','alembic_version','staging_ai_usage'];
BEGIN
    IF current_setting('prepmate.reviewed_dedicated_project', true) IS DISTINCT FROM 'yes' THEN
        RAISE EXCEPTION 'Explicit dedicated-project review acknowledgement required';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_default_acl d CROSS JOIN LATERAL aclexplode(d.defaclacl) a
        LEFT JOIN pg_roles r ON r.oid=a.grantee WHERE d.defaclrole=current_user::regrole
        AND d.defaclnamespace=0 AND d.defaclobjtype IN ('r','S')
        AND (a.grantee=0 OR r.rolname IN ('anon','authenticated','service_role'))) THEN
        RAISE EXCEPTION 'Unsafe global default grants require explicit operator review; schema revokes cannot override them';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'prepmate_runtime') THEN
        CREATE ROLE prepmate_runtime NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='prepmate_runtime'
        AND (rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls))
        OR EXISTS (SELECT 1 FROM pg_auth_members WHERE member='prepmate_runtime'::regrole)
        OR EXISTS (SELECT 1 FROM pg_class WHERE relowner='prepmate_runtime'::regrole) THEN
        RAISE EXCEPTION 'Unsafe existing runtime group; inspect instead of changing it automatically';
    END IF;
    GRANT USAGE ON SCHEMA public TO prepmate_runtime;
    IF EXISTS (SELECT 1 FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace
        WHERE e.extname='vector' AND n.nspname='extensions') THEN
        GRANT USAGE ON SCHEMA extensions TO prepmate_runtime;
    END IF;
    REVOKE CREATE ON SCHEMA public FROM PUBLIC, prepmate_runtime;
    FOR api_role IN SELECT rolname FROM pg_roles WHERE rolname IN ('anon','authenticated','service_role') LOOP
        EXECUTE format('REVOKE CREATE ON SCHEMA public FROM %I', api_role);
    END LOOP;
    FOREACH target IN ARRAY targets LOOP
        IF to_regclass(format('public.%I', target)) IS NULL THEN
            RAISE EXCEPTION 'Missing migrated table: %', target;
        END IF;
        IF (SELECT relowner FROM pg_class WHERE oid=to_regclass(format('public.%I',target))) <> current_user::regrole THEN
            RAISE EXCEPTION 'Run hardening as the actual migration owner of %', target;
        END IF;
        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename=target
            AND (policyname <> 'prepmate_backend_only' OR roles <> ARRAY['prepmate_runtime']::name[]
                OR cmd <> 'ALL' OR qual <> 'true' OR with_check <> 'true' OR permissive <> 'PERMISSIVE')) THEN
            RAISE EXCEPTION 'Unreviewed RLS policy on %; no policies were removed', target;
        END IF;
        EXECUTE format('REVOKE ALL ON TABLE public.%I FROM PUBLIC', target);
        EXECUTE format('REVOKE ALL ON TABLE public.%I FROM prepmate_runtime', target);
        FOREACH api_role IN ARRAY ARRAY['anon','authenticated','service_role'] LOOP
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname=api_role) THEN
                EXECUTE format('REVOKE ALL ON TABLE public.%I FROM %I', target, api_role);
            END IF;
        END LOOP;
        -- Columns can have independent grants; never leave an alternate path.
        FOR api_role IN SELECT attname FROM pg_attribute WHERE attrelid=to_regclass(format('public.%I',target)) AND attnum>0 AND NOT attisdropped LOOP
            EXECUTE format('REVOKE ALL (%I) ON TABLE public.%I FROM PUBLIC, prepmate_runtime', api_role, target);
            FOR sequence_name IN SELECT rolname FROM pg_roles WHERE rolname IN ('anon','authenticated','service_role') LOOP
                EXECUTE format('REVOKE ALL (%I) ON TABLE public.%I FROM %I', api_role, target, sequence_name);
            END LOOP;
        END LOOP;
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', target);
        EXECUTE format('ALTER TABLE public.%I FORCE ROW LEVEL SECURITY', target);
        IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename=target AND policyname='prepmate_backend_only') THEN
            EXECUTE format('CREATE POLICY prepmate_backend_only ON public.%I TO prepmate_runtime USING (true) WITH CHECK (true)', target);
        END IF;
        IF target IN ('chunks','alembic_version') THEN
            EXECUTE format('GRANT SELECT ON TABLE public.%I TO prepmate_runtime', target);
        ELSIF target='staging_ai_usage' THEN
            EXECUTE format('GRANT SELECT, INSERT, UPDATE ON TABLE public.%I TO prepmate_runtime', target);
        ELSE
            EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.%I TO prepmate_runtime', target);
        END IF;
        -- Only sequences owned by these tables; no unrelated provider objects.
        FOR sequence_name IN SELECT format('%I.%I', ns.nspname, seq.relname)
            FROM pg_class seq JOIN pg_namespace ns ON ns.oid=seq.relnamespace
            JOIN pg_depend dep ON dep.objid=seq.oid AND dep.classid='pg_class'::regclass
            WHERE seq.relkind='S' AND dep.refobjid=to_regclass(format('public.%I',target)) AND dep.deptype IN ('a','i') LOOP
            EXECUTE format('REVOKE ALL ON SEQUENCE %s FROM PUBLIC, prepmate_runtime', sequence_name);
            FOREACH api_role IN ARRAY ARRAY['anon','authenticated','service_role'] LOOP
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname=api_role) THEN
                    EXECUTE format('REVOKE ALL ON SEQUENCE %s FROM %I', sequence_name, api_role);
                END IF;
            END LOOP;
            IF target NOT IN ('chunks','alembic_version','staging_ai_usage') THEN
                EXECUTE format('GRANT USAGE, SELECT ON SEQUENCE %s TO prepmate_runtime', sequence_name);
            END IF;
        END LOOP;
    END LOOP;
    -- Applies to THIS migration owner, not every Supabase role.
    ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM PUBLIC;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM PUBLIC;
    FOREACH api_role IN ARRAY ARRAY['anon','authenticated','service_role'] LOOP
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname=api_role) THEN
            EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM %I', api_role);
            EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM %I', api_role);
        END IF;
    END LOOP;
END $$;
COMMIT;

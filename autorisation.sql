CREATE POLICY "autoriser insertion mesures"
ON public.mesures
FOR INSERT
TO anon
WITH CHECK (true);



CREATE POLICY "autoriser lecture mesures"
ON public.mesures
FOR SELECT
TO anon
USING (true);



GRANT SELECT, INSERT
ON TABLE public.mesures
TO anon;

--parceque j'ai utilisé upsert
GRANT SELECT, INSERT, UPDATE ON TABLE public.mesures TO anon;



ALTER TABLE public.mesures
ADD CONSTRAINT mesures_capteur_time_unique
UNIQUE (capteur_id, time);




GRANT SELECT, INSERT, UPDATE
ON TABLE public.mesures
TO anon;

CREATE POLICY "anon_select_mesures"
ON public.mesures
FOR SELECT
TO anon
USING (true);

CREATE POLICY "anon_insert_mesures"
ON public.mesures
FOR INSERT
TO anon
WITH CHECK (true);

CREATE POLICY "anon_update_mesures"
ON public.mesures
FOR UPDATE
TO anon
USING (true)
WITH CHECK (true);





CREATE OR REPLACE FUNCTION public.ajouter_mesures(
    nouvelles_mesures jsonb
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    nb_ajoutees integer;
BEGIN

    INSERT INTO public.mesures
    SELECT *
    FROM jsonb_populate_recordset(
        NULL::public.mesures,
        nouvelles_mesures
    )
    ON CONFLICT (capteur_id, time)
    DO NOTHING;

    GET DIAGNOSTICS nb_ajoutees = ROW_COUNT;

    RETURN nb_ajoutees;

END;
$$;

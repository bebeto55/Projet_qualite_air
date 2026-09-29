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

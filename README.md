# Projet_qualite_air
Ce projet à pour objectif de déterminer la qualité de l'air et d'afficher une prédiction pour le lendemain






temperature_2m (en °C)
relative_humidity_2m (en %)
wind_speed_10m (en km/h)
wind_direction_10m (en degrés, 0° = Nord)
precipitation (en mm)




Pour utiliser le notebook, 
1-n'oubliez pas de créer votre token : https://aqicn.org/data-platform/token/
après l'avoir reçus, vous créez un dossier .streamlit et à l'intérieur un fichier secrets.toml contenant : WQAI_token = "votre token" 
*********************structure***************
projet/.streamlit/secrets.toml


2-n'oubliez pas de décommenter !pip install sweetviz il fait pareil
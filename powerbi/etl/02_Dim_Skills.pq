// ============================================================================
// Dim_Skills  (catalogo de 35 skills con categoria y descripcion)
// ----------------------------------------------------------------------------
// Tabla estatica inline — no necesita CSV. Si se agregan skills en utils.py
// del pipeline Python, replicar aqui.
// ============================================================================
let
    Origen = #table(
        type table [
            skill           = text,
            skill_id        = text,
            categoria       = text,
            tipo            = text,
            es_premium      = logical
        ],
        {
            // ───── Lenguajes de programacion ─────
            {"Python",          "skill_python",          "Lenguajes",        "Programacion", false},
            {"R",               "skill_r",               "Lenguajes",        "Programacion", false},
            {"SAS",             "skill_sas",             "Lenguajes",        "Estadistica",  false},
            {"SPSS",            "skill_spss",            "Lenguajes",        "Estadistica",  false},
            {"VBA",             "skill_vba",             "Lenguajes",        "Office",       false},

            // ───── Bases de datos / Query ─────
            {"SQL",             "skill_sql",             "Bases de Datos",   "Query",        false},
            {"Snowflake",       "skill_snowflake",       "Bases de Datos",   "Data Warehouse", true},
            {"BigQuery",        "skill_bigquery",        "Bases de Datos",   "Data Warehouse", true},
            {"Redshift",        "skill_redshift",        "Bases de Datos",   "Data Warehouse", true},
            {"Databricks",      "skill_databricks",      "Bases de Datos",   "Lakehouse",    true},

            // ───── Big Data ─────
            {"Spark",           "skill_spark",           "Big Data",         "Procesamiento", true},
            {"Hadoop",          "skill_hadoop",          "Big Data",         "Procesamiento", false},

            // ───── Orquestacion / Transformacion ─────
            {"Airflow",         "skill_airflow",         "Orquestacion",     "Pipelines",    true},
            {"dbt",             "skill_dbt",             "Orquestacion",     "Transformacion", true},

            // ───── Cloud ─────
            {"AWS",             "skill_aws",             "Cloud",            "Hyperscaler",  true},
            {"Azure",           "skill_azure",           "Cloud",            "Hyperscaler",  true},
            {"GCP",             "skill_gcp",             "Cloud",            "Hyperscaler",  true},

            // ───── DevOps ─────
            {"Docker",          "skill_docker",          "DevOps",           "Contenedores", false},
            {"Kubernetes",      "skill_kubernetes",      "DevOps",           "Orquestacion", true},
            {"Git",             "skill_git",             "DevOps",           "Version Control", false},

            // ───── BI / Visualizacion ─────
            {"Excel",           "skill_excel",           "BI",               "Visualizacion", false},
            {"Power BI",        "skill_power_bi",        "BI",               "Visualizacion", false},
            {"Tableau",         "skill_tableau",         "BI",               "Visualizacion", false},
            {"Looker",          "skill_looker",          "BI",               "Visualizacion", false},
            {"DAX",             "skill_dax",             "BI",               "Lenguaje BI",  false},
            {"Power Query",     "skill_power_query",     "BI",               "ETL",          false},

            // ───── Automatizacion ─────
            {"Power Automate",  "skill_power_automate",  "Automatizacion",   "RPA",          false},

            // ───── Librerias Python ─────
            {"Pandas",          "skill_pandas",          "Librerias",        "Data Wrangling", false},
            {"NumPy",           "skill_numpy",           "Librerias",        "Calculo",      false},
            {"scikit-learn",    "skill_scikit_learn",    "Librerias",        "ML",           false},
            {"TensorFlow",      "skill_tensorflow",      "Librerias",        "Deep Learning", true},
            {"PyTorch",         "skill_pytorch",         "Librerias",        "Deep Learning", true},

            // ───── ML / IA ─────
            {"Machine Learning","skill_machine_learning","ML/AI",            "Concepto",     true},
            {"Deep Learning",   "skill_deep_learning",   "ML/AI",            "Concepto",     true},
            {"NLP",             "skill_nlp",             "ML/AI",            "Concepto",     true}
        }
    )
in
    Origen

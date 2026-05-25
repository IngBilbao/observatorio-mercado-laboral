// ============================================================================
// Dim_Roles  (8 roles canonicos del catalogo del Observatorio)
// ============================================================================
let
    Origen = #table(
        type table [
            rol             = text,
            categoria_rol   = text,
            seniority_typ   = text,
            orden_display   = Int64.Type
        ],
        {
            {"Data Analyst",       "Analisis",   "Junior-Mid",      1},
            {"BI Analyst",         "Analisis",   "Junior-Senior",   2},
            {"Business Analyst",   "Negocio",    "Junior-Mid",      3},
            {"Financial Analyst",  "Negocio",    "Junior-Senior",   4},
            {"Data Scientist",     "Ciencia",    "Mid-Senior",      5},
            {"ML Engineer",        "Ingenieria", "Mid-Lead",        6},
            {"Data Engineer",      "Ingenieria", "Mid-Senior",      7},
            {"Analytics Engineer", "Ingenieria", "Mid-Senior",      8}
        }
    )
in
    Origen

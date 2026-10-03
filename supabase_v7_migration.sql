-- Run after earlier schema/migrations.
create index if not exists idx_companies_pec_license on companies(pec_license);
create index if not exists idx_companies_name on companies(company_name);
create index if not exists idx_matches_company_created on matches(company_name,created_at desc);

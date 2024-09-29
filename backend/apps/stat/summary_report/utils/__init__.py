INCOME_SQL = """
select mc, company_name, first_name, last_name, sum(wn) amount_requested, sum(kwp) amount_granted, count(1) cnt
from (
         select to_char(dd.creation_date, 'YYYY-MM') mc,
                aa_wn.value::float wn,
                aa_kwp.value::float kwp,
                uu.company_name,
                uu.first_name,
                uu.last_name,
                coalesce(uu.id,0) user_id
         from crm.document dd
                  left outer join crm.document_attribute aa_adv on aa_adv.document_id = dd.id and aa_adv.id_attribute = {adviser_id}
                  left outer join crm.document_attribute aa_brk on aa_brk.document_id = dd.id and aa_brk.id_attribute = {broker_id} 
                  left outer join crm.document_attribute aa_wn on aa_wn.document_id = dd.id and aa_wn.id_attribute = {amount_requested_id}
                  left outer join crm.document_attribute aa_kwp on aa_kwp.document_id = dd.id and aa_wn.id_attribute = {amount_granted_id}
                  left outer join crm.document_attribute aa_agr_type on aa_agr_type.document_id = dd.id and aa_agr_type.id_attribute = {agreement_type_id}
                  left outer join crm."user" uu on case when aa_adv.value = '' then null else aa_adv.value::int end = uu.id                  
                  left outer join crm."user" uu_owner on dd.id_owner=uu_owner.id    
         where dd.id_type = 1
         {date_from} 
         {date_to} 
         {advisers}
         {brokers}
         {status}
         {bussiness_type}    
         {agreement_type}                                                          
     ) t
group by mc, user_id, company_name, first_name, last_name
order by mc desc, last_name
"""

INCOME_SQL_3 = """
select concat(uu.last_name, ' ', uu.first_name)                                   adviser,
       to_char(dd.creation_date, 'YYYYMM')                                   mc,
       coalesce(case when aa_wn.value = '' then 0 else aa_wn.value::float end, 0) amount_req,
       coalesce(case when aa_gr.value = '' then 0 else aa_gr.value::float end, 0) amount_gr,
       coalesce(case when aa_cm.value = '' then 0 else aa_cm.value::float end, 0) commission
from crm.document dd
         left outer join crm.document_attribute aa_gr on aa_gr.id_attribute = {amount_granted_id} and aa_gr.document_id = dd.id
         left outer join crm.document_attribute aa_wn on aa_wn.id_attribute = {amount_requested_id} and aa_wn.document_id = dd.id
         left outer join crm.document_attribute aa_cm on aa_cm.id_attribute = {commission_id} and aa_cm.document_id = dd.id
         left outer join crm.document_attribute aa_agr_type on aa_agr_type.document_id = dd.id and aa_agr_type.id_attribute = {agreement_type_id}
         left outer join crm.document_attribute aa_brk on aa_brk.id_attribute = {broker_id} and aa_brk.document_id = dd.id,
     crm.document_attribute aa_adv,
     crm.user uu,
     crm.user uu_owner
where aa_adv.id_attribute = {adviser_id}
  and aa_adv.document_id = dd.id
  and dd.id_type = 1
  and uu_owner.id=dd.id_owner
  and case when aa_adv.value = '' then null else aa_adv.value::int end = uu.id
  {date_from} 
  {date_to} 
  {advisers}
  {brokers}
  {status}
  {bussiness_type}
  {agreement_type}   
"""
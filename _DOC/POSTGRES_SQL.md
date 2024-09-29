# Postgres recusive query example
```sql
insert into crm.document_type_attribute_feature(visible, editable, required, id_document_type_attribute, id_document_type_status, value_operator)
select true, false, false, aa.id, 70, false
from crm.document_type_attribute aa
where aa.id_document_type = 26
  and aa.id not in (with recursive atr(id, parent) as (select dd.id, dd.id_parent
                                                       from crm.document_type_attribute dd
                                                       where id = 3293
                                                       union all
                                                       select dd.id, dd.id_parent
                                                       from atr t,
                                                            crm.document_type_attribute dd
                                                       where t.id = dd.id_parent)
                    select id
                    from atr
)

```
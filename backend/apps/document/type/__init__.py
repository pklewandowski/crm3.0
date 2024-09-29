DOCUMENT_PROCESS_FLOW_RAW_SQL_QUERY = \
"""SELECT *
        FROM ( 
            SELECT dd.history_id id,
              lag(dd.id_status)
              OVER (
                PARTITION BY dd.id
                ORDER BY dd.history_date),
              dd.id_status,
              dd.history_date,
              dd.history_user_id
            FROM h_document dd
            WHERE dd.id = %s
          )t
        WHERE lag ISNULL OR id_status <> lag
"""

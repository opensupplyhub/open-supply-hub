'''
1. What if creting updating production location takes time on OS Hub, and we need to wait for it to be created / updated before we can sync it to RBA?
2. Shall this script always run in a separate AWS job?
3. Shall we block RBA database from being updated while this script is running?
4. What if pipeline crashed while running this script?
5. How to monitor the status of this script and diffs between OS Hub and RBA?
6. Shall we have an ability to stop this script?
7. Is it possible to revert this script to the previous revision?
8. It looks like we need a separate database table to store the status of the sync process (and related information).
9. If there will be a table to store sync status, we need to apply respected UI (probably, in Django admin panel).
10. Shall it be bulc sync impicitly or it is better to check specific tables to be updated? For this, we need to apply specific pattern.
11. How to test this locally? Shall we use docker with local DB that will emulate RBA DB?
'''


def main():
    # Connect to the DB instance of OS Hub once shcedule OR once producrion location added / updated
    os_conn = connect_to_os_hub()
    rba_conn = connect_to_rba()

    os_data = fetch_production_locations(os_conn)
    rba_data = fetch_existing_locations(rba_conn)

    changes = determine_changes(os_data, rba_data)
    apply_updates(rba_conn, changes)

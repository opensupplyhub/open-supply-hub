import React from 'react';
import Button from '@material-ui/core/Button';

import { pageRangeLabel } from './utils';
import styles from './styles';

/* Previous / next paging for the organization tables. */
const Pager = ({ page, pageSize, count, onChange, disabled }) => (
    <div style={styles.pager}>
        <span>{pageRangeLabel(page, pageSize, count)}</span>
        <Button
            size="small"
            disabled={disabled || page <= 1}
            onClick={() => onChange(page - 1)}
        >
            Previous
        </Button>
        <Button
            size="small"
            disabled={disabled || page * pageSize >= count}
            onClick={() => onChange(page + 1)}
        >
            Next
        </Button>
    </div>
);

export default Pager;

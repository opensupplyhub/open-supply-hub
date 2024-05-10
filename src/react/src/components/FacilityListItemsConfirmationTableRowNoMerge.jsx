import { React } from 'react';
import { string } from 'prop-types';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';

import { listTableCellStyles } from '../util/styles';

const FacilityListItemsConfirmationTableRowNoMerge = ({ className }) => (
    <TableRow
        hover={false}
        style={{
            background: '#dcfbff',
            verticalAlign: 'top',
        }}
        className={className}
    >
        <TableCell padding="default" variant="head" colSpan={4} />
        <TableCell
            padding="default"
            variant="head"
            colSpan={2}
            style={{
                ...listTableCellStyles.noMergeCellStyles,
                textAlign: 'left',
            }}
        >
            No facilities available to merge
        </TableCell>
        <TableCell padding="default" variant="head" />
    </TableRow>
);

FacilityListItemsConfirmationTableRowNoMerge.propTypes = {
    className: string.isRequired,
};

export default FacilityListItemsConfirmationTableRowNoMerge;

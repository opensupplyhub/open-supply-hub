import { React } from 'react';
import { bool, number, func, string, shape, arrayOf } from 'prop-types';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import Checkbox from '@material-ui/core/Checkbox';
import CellElement from './CellElement';
import ShowOnly from './ShowOnly';

import {
    listTableCellStyles,
    confirmRejectMatchRowStyles,
} from '../util/styles';

import { makeFacilityDetailLink } from '../util/util';
import {
    facilityMatchStatusChoicesEnum,
    CONFIRM_ACTION,
} from '../util/constants';

const FacilityListItemsConfirmationTableRowItem = ({
    id,
    os_id, // eslint-disable-line camelcase
    name,
    status,
    className,
    activeCheckboxes,
    address,
    isCheckboxDisabled,
    confidence,
    readOnly,
    toggleCheckbox,
    action,
}) => (
    <TableRow
        hover={false}
        style={{
            background: '#dcfbff',
            verticalAlign: 'top',
        }}
        className={className}
        key={id}
    >
        <TableCell padding="default" variant="head" colSpan={2} />
        <TableCell padding="default" style={listTableCellStyles.nameCellStyles}>
            <CellElement item={name} linkURL={makeFacilityDetailLink(os_id)} />
        </TableCell>
        <TableCell
            padding="default"
            style={listTableCellStyles.addressCellStyles}
        >
            <CellElement item={address} />
        </TableCell>
        <TableCell
            padding="default"
            colSpan={2}
            variant="head"
            style={{
                ...listTableCellStyles.headerCellStyles,
                textAlign: 'left',
            }}
        >
            <div>
                <ShowOnly when={!readOnly}>
                    {status !== facilityMatchStatusChoicesEnum.PENDING ? (
                        <div
                            key={id}
                            style={confirmRejectMatchRowStyles.cellRowStyles}
                        >
                            <div
                                style={
                                    confirmRejectMatchRowStyles.cellActionStyles
                                }
                            >
                                <div>{status}</div>
                            </div>
                        </div>
                    ) : (
                        <Checkbox
                            onChange={() =>
                                toggleCheckbox({
                                    id,
                                    os_id,
                                    address,
                                    name,
                                    confidence,
                                })
                            }
                            checked={
                                action === CONFIRM_ACTION
                                    ? activeCheckboxes[0]?.id === id // eslint-disable-line camelcase
                                    : activeCheckboxes.some(
                                          activeItem => activeItem.id === id, // eslint-disable-line camelcase
                                      )
                            }
                            disabled={isCheckboxDisabled(id)}
                        />
                    )}
                </ShowOnly>
            </div>
        </TableCell>
        <TableCell
            padding="default"
            variant="head"
            style={{
                ...listTableCellStyles.headerCellStyles,
                textAlign: 'left',
                paddingLeft: '65px',
            }}
        >
            <b>{confidence}</b>
        </TableCell>
    </TableRow>
);

FacilityListItemsConfirmationTableRowItem.propTypes = {
    id: number.isRequired,
    os_id: number.isRequired, // eslint-disable-line camelcase
    name: string.isRequired,
    status: string.isRequired,
    className: string.isRequired,
    activeCheckboxes: arrayOf(
        shape({
            name: string,
            address: string,
        }),
    ).isRequired,
    address: number.isRequired,
    isCheckboxDisabled: bool.isRequired,
    confidence: string.isRequired,
    readOnly: bool.isRequired,
    toggleCheckbox: func.isRequired,
    action: string.isRequired,
};

export default FacilityListItemsConfirmationTableRowItem;

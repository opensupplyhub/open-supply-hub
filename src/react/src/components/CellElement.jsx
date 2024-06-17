import React, { Component } from 'react';
import {
    bool,
    func,
    number,
    oneOf,
    oneOfType,
    shape,
    string,
} from 'prop-types';
import { Link } from 'react-router-dom';

import { facilityMatchStatusChoicesEnum } from '../util/constants';

import { confirmRejectMatchRowStyles } from '../util/styles';

export default class CellElement extends Component {
    // TODO split the logic of this component so it won't have multiple render outputs
    render() {
        const {
            item,
            errorState,
            hasActions,
            stringIsHidden,
            linkURL,
        } = this.props;

        if (!hasActions) {
            const insetComponent = (() => {
                if (stringIsHidden) {
                    return ' ';
                }

                if (linkURL) {
                    return (
                        <Link to={linkURL} href={linkURL}>
                            {item}
                        </Link>
                    );
                }

                return item;
            })();

            return (
                <div
                    key={item}
                    style={
                        errorState
                            ? confirmRejectMatchRowStyles.errorCellRowStyles
                            : null
                    }
                >
                    {insetComponent}
                </div>
            );
        }

        if (item.status !== facilityMatchStatusChoicesEnum.PENDING) {
            return (
                <div
                    key={item.id}
                    style={confirmRejectMatchRowStyles.cellRowStyles}
                >
                    <div style={confirmRejectMatchRowStyles.cellActionStyles}>
                        <div>{item.status}</div>
                    </div>
                </div>
            );
        }

        return null;
    }
}

CellElement.defaultProps = {
    errorState: false,
    hasActions: false,
    stringIsHidden: false,
    linkURL: null,
};

CellElement.propTypes = {
    item: oneOfType([
        number,
        string,
        shape({
            id: number.isRequired,
            confirmMatch: func.isRequired,
            rejectMatch: func.isRequired,
            status: oneOf(Object.values(facilityMatchStatusChoicesEnum))
                .isRequired,
            matchName: string.isRequird,
            matchAddress: string.isRequired,
            itemName: string.isRequired,
            itemAddress: string.isRequired,
        }),
    ]).isRequired,
    errorState: bool,
    hasActions: bool,
    stringIsHidden: bool,
    linkURL: string,
};

import React from 'react';
import {
    arrayOf,
    bool,
    func,
    number,
    string,
    oneOfType,
    element,
} from 'prop-types';
import { connect } from 'react-redux';
import CircularProgress from '@material-ui/core/CircularProgress';
import MaterialButton from '@material-ui/core/Button';
import { toast } from 'react-toastify';
import { withStyles } from '@material-ui/core/styles';
import Tooltip from '@material-ui/core/Tooltip';
import ControlledTextInput from './ControlledTextInput';
import Button from './Button';
import FeatureFlag from './FeatureFlag';
import ContributeFormSelectListToReplace from './ContributeFormSelectListToReplace';
import ListUploadErrors from './ListUploadErrors';

import COLOURS from '../util/COLOURS';

import {
    getValueFromEvent,
    getFileFromInputRef,
    getFileNameFromInputRef,
    makeFacilityListItemsDetailLink,
} from '../util/util';

import {
    contributeFormFields,
    contributeFieldsEnum,
    DISABLE_LIST_UPLOADING,
} from '../util/constants';

import { useFileUploadHandler } from '../util/hooks';

import {
    updateFileUploadName,
    updateFileUploadDescription,
    updateFileUploadFileName,
    updateFileUploadListToReplaceID,
    uploadFile,
    resetUploadState,
} from '../actions/upload';

import {
    fetchUserFacilityLists,
    resetUserFacilityLists,
} from '../actions/facilityLists';

import { facilityListPropType } from '../util/propTypes';

const StyledTooltip = withStyles({
    tooltip: {
        color: 'rgba(0, 0, 0, 0.8)',
        fontSize: '0.875rem',
        backgroundColor: 'white',
        border: 'solid rgba(0, 0, 0, 0.25)',
        borderRadius: '10px',
        padding: '10px',
        lineHeight: '1',
    },
})(Tooltip);

const contributeFormStyles = Object.freeze({
    fileNameText: Object.freeze({
        color: COLOURS.LIGHT_BLUE,
        fontSize: '12px',
        display: 'block',
        marginTop: '8px',
        fontStyle: 'italic',
    }),
    fileInputHidden: Object.freeze({
        display: 'none',
        visibility: 'hidden',
    }),
});

const ContributeForm = ({
    name,
    description,
    filename,
    replaces,
    fetching,
    error,
    updateName,
    updateDescription,
    updateFileName,
    updateListToReplace,
    uploadList,
    fetchLists,
    resetForm,
    facilityLists,
    fetchingFacilityLists,
}) => {
    const { fileInput } = useFileUploadHandler({
        resetForm,
        fetching,
        error,
        fetchLists,
        toast,
    });

    const selectFile = () => fileInput.current.click();
    const updateSelectedFileName = () => updateFileName(fileInput);
    const handleUploadList = () => uploadList(fileInput);

    const errorMessages =
        error && error.length ? <ListUploadErrors errors={error} /> : null;

    const formInputs = contributeFormFields.map(field => (
        <div key={field.id} className="form__field">
            <label htmlFor={field.id} className="form__label">
                {field.label}
            </label>
            <span style={{ color: 'red' }}>{field.required ? ' *' : ''}</span>
            <ControlledTextInput
                id={field.id}
                type={field.type}
                hint={field.hint}
                placeholder={field.placeholder}
                onChange={
                    field.id === contributeFieldsEnum.name
                        ? updateName
                        : updateDescription
                }
                value={
                    field.id === contributeFieldsEnum.name ? name : description
                }
            />
        </div>
    ));

    const submitButtonIsDisabled = fetching || fetchingFacilityLists;

    const replacesSection =
        facilityLists && facilityLists.length ? (
            <ContributeFormSelectListToReplace
                lists={facilityLists}
                replaces={replaces}
                handleChange={updateListToReplace}
            />
        ) : null;

    return (
        <div className="control-panel__group">
            {formInputs}
            <div className="form__field">
                <MaterialButton
                    onClick={selectFile}
                    type="button"
                    variant="outlined"
                    color="primary"
                    className="outlined-button"
                    disableRipple
                >
                    Select Facility List File
                </MaterialButton>
                <p style={contributeFormStyles.fileNameText}>{filename}</p>
                <input
                    type="file"
                    accept=".csv,.xlsx"
                    ref={fileInput}
                    style={contributeFormStyles.fileInputHidden}
                    onChange={updateSelectedFileName}
                />
            </div>
            {replacesSection}
            <div className="form__field cursor">
                {errorMessages}
                {fetching ? (
                    <CircularProgress size={30} />
                ) : (
                    <FeatureFlag
                        flag={DISABLE_LIST_UPLOADING}
                        alternative={
                            <Button
                                onClick={handleUploadList}
                                disabled={submitButtonIsDisabled}
                                text="SUBMIT"
                                variant="contained"
                                disableRipple
                            />
                        }
                    >
                        <StyledTooltip
                            title="Open Supply Hub is undergoing maintenance and not accepting new data at the moment. Please try again in a few minutes."
                            placement="right"
                        >
                            <span>
                                <Button
                                    disabled
                                    text="SUBMIT"
                                    variant="contained"
                                    disableRipple
                                    onClick={() => {}}
                                />
                            </span>
                        </StyledTooltip>
                    </FeatureFlag>
                )}
            </div>
        </div>
    );
};

ContributeForm.defaultProps = {
    error: null,
};

ContributeForm.propTypes = {
    name: string.isRequired,
    description: string.isRequired,
    filename: string.isRequired,
    replaces: number.isRequired,
    fetching: bool.isRequired,
    error: arrayOf(oneOfType([element, string])),
    updateName: func.isRequired,
    updateDescription: func.isRequired,
    updateFileName: func.isRequired,
    updateListToReplace: func.isRequired,
    uploadList: func.isRequired,
    facilityLists: arrayOf(facilityListPropType).isRequired,
    fetchingFacilityLists: bool.isRequired,
    fetchLists: func.isRequired,
    resetForm: func.isRequired,
};

const mapStateToProps = ({
    upload: {
        form: { name, description, filename, replaces },
        fetching,
        error,
    },
    facilityLists: { facilityLists, fetching: fetchingFacilityLists },
}) => ({
    name,
    description,
    filename,
    replaces,
    fetching,
    error,
    facilityLists,
    fetchingFacilityLists,
});

const mapDispatchToProps = (dispatch, { history: { push } }) => ({
    updateName: e => dispatch(updateFileUploadName(getValueFromEvent(e))),
    updateDescription: e =>
        dispatch(updateFileUploadDescription(getValueFromEvent(e))),
    updateFileName: r =>
        dispatch(updateFileUploadFileName(getFileNameFromInputRef(r))),
    updateListToReplace: e =>
        dispatch(updateFileUploadListToReplaceID(getValueFromEvent(e))),
    uploadList: r =>
        dispatch(
            uploadFile(getFileFromInputRef(r), id =>
                push(makeFacilityListItemsDetailLink(id)),
            ),
        ),
    fetchLists: () => dispatch(fetchUserFacilityLists()),
    resetForm: () => {
        dispatch(resetUserFacilityLists());
        return dispatch(resetUploadState());
    },
});

export default connect(mapStateToProps, mapDispatchToProps)(ContributeForm);

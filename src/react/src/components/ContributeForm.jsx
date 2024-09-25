import React, { useState } from 'react';
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

import ControlledTextInput from './ControlledTextInput';
import Button from './Button';
import ContributeFormSelectListToReplace from './ContributeFormSelectListToReplace';

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
    listsRoute,
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
    fetchingFeatureFlags,
}) => {
    const [hasUploadErrorBeenHandled, setHasUploadErrorBeenHandled] = useState(
        false,
    );
    const { fileInput } = useFileUploadHandler({
        resetForm,
        fetching,
        error,
        fetchLists,
        listsRoute,
        hasUploadErrorBeenHandled,
        setHasUploadErrorBeenHandled,
        toast,
    });

    const selectFile = () => fileInput.current.click();
    const updateSelectedFileName = () => updateFileName(fileInput);
    const handleUploadList = () => uploadList(fileInput);

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
            <div className="form__field">
                {fetching || fetchingFeatureFlags ? (
                    <CircularProgress size={30} />
                ) : (
                    <Button
                        onClick={handleUploadList}
                        disabled={submitButtonIsDisabled}
                        text="SUBMIT"
                        variant="contained"
                        disableRipple
                    />
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
    fetchingFeatureFlags: bool.isRequired,
};

const mapStateToProps = ({
    upload: {
        form: { name, description, filename, replaces },
        fetching,
        error,
    },
    facilityLists: { facilityLists, fetching: fetchingFacilityLists },
    featureFlags: { fetching: fetchingFeatureFlags },
}) => ({
    name,
    description,
    filename,
    replaces,
    fetching,
    error,
    facilityLists,
    fetchingFacilityLists,
    fetchingFeatureFlags,
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

import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';

import {
    logErrorAndDispatchFailure,
    makeUploadFacilityListsURL,
    createUploadFormErrorMessages,
} from '../util/util';

import { contributeReplacesNoneSelectionID } from '../util/constants';

export const updateFileUploadName = createAction('UPDATE_FILE_UPLOAD_NAME');
export const updateFileUploadDescription = createAction(
    'UPDATE_FILE_UPLOAD_DESCRIPTION',
);
export const updateFileUploadFileName = createAction(
    'UPDATE_FILE_UPLOAD_FILE_NAME',
);
export const updateFileUploadListToReplaceID = createAction(
    'UPDATE_FILE_UPLOAD_LIST_TO_REPLACE_ID',
);

export const startUploadFile = createAction('START_UPLOAD_FILE');
export const failUploadFile = createAction('FAIL_UPLOAD_FILE');
export const completeUploadFile = createAction('COMPLETE_UPLOAD_FILE');

export const resetUploadState = createAction('RESET_UPLOAD_STATE');

export function uploadFile(file = null, redirectToListDetail) {
    return (dispatch, getState) => {
        dispatch(startUploadFile());

        const {
            upload: {
                form: { name, description, replaces },
            },
            featureFlags: {
                flags: {
                    use_old_upload_list_endpoint: useOldUploadListEndpoint,
                },
            },
        } = getState();

        const requiredDataErrors = createUploadFormErrorMessages(name, file);

        if (requiredDataErrors.length) {
            return dispatch(failUploadFile(requiredDataErrors));
        }

        const formData = new FormData();

        formData.append('file', file);

        // Remove extra spaces if needed
        const formattedName = name.replace(/\s+/g, ' ').trim();
        formData.append('name', formattedName);

        if (description) {
            formData.append('description', description);
        }

        if (replaces !== contributeReplacesNoneSelectionID) {
            formData.append('replaces', replaces);
        }

        return apiRequest
            .post(
                makeUploadFacilityListsURL(useOldUploadListEndpoint),
                formData,
            )
            .then(({ data: { id } }) => {
                dispatch(completeUploadFile());
                redirectToListDetail(id);
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented uploading that file',
                        failUploadFile,
                    ),
                ),
            );
    };
}

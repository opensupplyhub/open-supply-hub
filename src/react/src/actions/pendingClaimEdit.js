import { createAction } from 'redux-act';

import apiRequest from '../util/apiRequest';

import {
    makePendingClaimURL,
    makePendingClaimAttachmentsURL,
    makePendingClaimAttachmentURL,
    logErrorAndDispatchFailure,
} from '../util/util';

import {
    pendingClaimApiToFormData,
    buildPendingClaimPatchPayload,
} from '../components/PendingClaimEdit/utils';

export const startFetchPendingClaim = createAction('START_FETCH_PENDING_CLAIM');
export const failFetchPendingClaim = createAction('FAIL_FETCH_PENDING_CLAIM');
export const completeFetchPendingClaim = createAction(
    'COMPLETE_FETCH_PENDING_CLAIM',
);

export const updatePendingClaimFormField = createAction(
    'UPDATE_PENDING_CLAIM_FORM_FIELD',
);

export const startSavePendingClaim = createAction('START_SAVE_PENDING_CLAIM');
export const failSavePendingClaim = createAction('FAIL_SAVE_PENDING_CLAIM');
export const completeSavePendingClaim = createAction(
    'COMPLETE_SAVE_PENDING_CLAIM',
);

export const startDeletePendingClaimAttachment = createAction(
    'START_DELETE_PENDING_CLAIM_ATTACHMENT',
);
export const failDeletePendingClaimAttachment = createAction(
    'FAIL_DELETE_PENDING_CLAIM_ATTACHMENT',
);
export const completeDeletePendingClaimAttachment = createAction(
    'COMPLETE_DELETE_PENDING_CLAIM_ATTACHMENT',
);

export const resetPendingClaimEdit = createAction('RESET_PENDING_CLAIM_EDIT');

export function fetchPendingClaim(claimID) {
    return dispatch => {
        dispatch(startFetchPendingClaim());

        return apiRequest
            .get(makePendingClaimURL(claimID))
            .then(({ data }) =>
                dispatch(
                    completeFetchPendingClaim({
                        data,
                        formData: pendingClaimApiToFormData(data),
                    }),
                ),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching this pending claim',
                        failFetchPendingClaim,
                    ),
                ),
            );
    };
}

/*
 * Saving a pending claim edit is up to two requests: newly picked
 * document files are uploaded first (multipart POST to the attachments
 * sub-resource), then the field edits go out as a JSON PATCH. The PATCH
 * response is the fresh pending-claim payload, which becomes the new
 * source of truth for the form.
 */
export function savePendingClaim(claimID) {
    return (dispatch, getState) => {
        const {
            pendingClaimEdit: { formData },
        } = getState();

        dispatch(startSavePendingClaim());

        const newFiles = [
            ...(formData.employmentVerificationDocuments || []),
            ...(formData.companyAddressVerificationDocuments || []),
        ];

        const uploadNewFiles = () => {
            if (newFiles.length === 0) {
                return Promise.resolve();
            }

            const postData = new FormData();
            newFiles.forEach(file => postData.append('files', file));

            return apiRequest.post(
                makePendingClaimAttachmentsURL(claimID),
                postData,
            );
        };

        return uploadNewFiles()
            .then(() =>
                apiRequest.patch(
                    makePendingClaimURL(claimID),
                    buildPendingClaimPatchPayload(formData),
                ),
            )
            .then(({ data }) =>
                dispatch(
                    completeSavePendingClaim({
                        data,
                        formData: pendingClaimApiToFormData(data),
                    }),
                ),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented saving your claim updates',
                        failSavePendingClaim,
                    ),
                ),
            );
    };
}

export function deletePendingClaimAttachment(claimID, attachmentID) {
    return dispatch => {
        dispatch(startDeletePendingClaimAttachment());

        return apiRequest
            .delete(makePendingClaimAttachmentURL(claimID, attachmentID))
            .then(({ data }) =>
                dispatch(completeDeletePendingClaimAttachment({ data })),
            )
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented removing this document',
                        failDeletePendingClaimAttachment,
                    ),
                ),
            );
    };
}

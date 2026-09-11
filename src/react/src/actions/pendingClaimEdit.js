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
 * Saving a pending claim edit is up to two requests: the field edits go
 * out as a JSON PATCH first, then newly picked document files are
 * uploaded (multipart POST to the attachments sub-resource). The last
 * response is the fresh pending-claim payload, which becomes the new
 * source of truth for the form.
 *
 * The PATCH deliberately runs FIRST: if it fails validation, nothing
 * has been uploaded yet, so the still-populated pickers can safely
 * retry without duplicating attachments. On the reverse ordering a
 * failed PATCH left the files already stored while the pickers kept
 * them, and the retry uploaded them a second time. If the upload step
 * fails instead, the retried PATCH is a no-op server-side (no changes,
 * no email, no claimant_updated_at stamp), so retrying is safe there
 * too.
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

        const uploadNewFiles = patchResponseData => {
            if (newFiles.length === 0) {
                return Promise.resolve({ data: patchResponseData });
            }

            const postData = new FormData();
            newFiles.forEach(file => postData.append('files', file));

            return apiRequest.post(
                makePendingClaimAttachmentsURL(claimID),
                postData,
            );
        };

        return apiRequest
            .patch(
                makePendingClaimURL(claimID),
                buildPendingClaimPatchPayload(formData),
            )
            .then(({ data }) => uploadNewFiles(data))
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

import { createAction } from 'redux-act';

// Prefetch data actions
export const startPrefetchClaimFormData = createAction(
    'START_PREFETCH_CLAIM_FORM_DATA',
);
export const completePrefetchClaimFormData = createAction(
    'COMPLETE_PREFETCH_CLAIM_FORM_DATA',
);
export const failPrefetchClaimFormData = createAction(
    'FAIL_PREFETCH_CLAIM_FORM_DATA',
);

// Step navigation actions
export const setActiveClaimFormStep = createAction(
    'SET_ACTIVE_CLAIM_FORM_STEP',
);
export const markStepComplete = createAction('MARK_CLAIM_FORM_STEP_COMPLETE');

// Form data actions
export const updateClaimFormField = createAction('UPDATE_CLAIM_FORM_FIELD');
export const setClaimFormData = createAction('SET_CLAIM_FORM_DATA');
export const resetClaimForm = createAction('RESET_CLAIM_FORM');

// Mock data prefetch function
// TODO: Replace with actual API call when backend is ready
export function fetchClaimFormData(osID) {
    return dispatch => {
        dispatch(startPrefetchClaimFormData());

        // Mock implementation - simulates API call
        setTimeout(() => {
            const mockData = {
                sectors: [
                    'Apparel',
                    'Textiles',
                    'Manufacturing',
                    'Agriculture',
                    'Automotive',
                ],
                processingTypes: [
                    'Cut & Sew',
                    'Dyeing',
                    'Finishing',
                    'Weaving',
                    'Knitting',
                ],
                affiliations: [
                    'Better Mills Program',
                    'Canopy',
                    'Sustainable Apparel Coalition',
                    'Fashion Revolution',
                ],
                certifications: [
                    'ISO 9001',
                    'GOTS',
                    'OEKO-TEX',
                    'WRAP',
                    'SA8000',
                ],
                facilityData: {
                    name: 'ABC Manufacturing Ltd.',
                    address: '123 Industrial Park Road',
                    osID,
                },
            };

            dispatch(completePrefetchClaimFormData(mockData));
        }, 500);

        // TODO: Uncomment when API is ready
        // return apiRequest
        //     .get(`/api/facilities/${osID}/`)
        //     .then(({ data }) => dispatch(completePrefetchClaimFormData(data)))
        //     .catch(err =>
        //         dispatch(
        //             logErrorAndDispatchFailure(
        //                 err,
        //                 'An error prevented fetching claim form data',
        //                 failPrefetchClaimFormData,
        //             ),
        //         ),
        //     );
    };
}

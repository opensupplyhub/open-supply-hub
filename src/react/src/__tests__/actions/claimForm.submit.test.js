import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import { submitClaimFormData } from '../../actions/claimForm';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { post: jest.fn() },
}));

const mockStore = configureStore([thunk]);
const OS_ID = 'TR2019083D9HN4X';

const submittedValues = (formData, key) => {
    const store = mockStore({ claimForm: { formData } });
    store.dispatch(submitClaimFormData(OS_ID, false));
    const [, postData] = apiRequest.post.mock.calls[0];
    return postData.getAll(key);
};

describe('submitClaimFormData', () => {
    // The test environment is node; setupTests.js provides a JSDOM
    // window, whose FormData and localStorage the action uses.
    beforeAll(() => {
        global.FormData = window.FormData;
        global.localStorage = window.localStorage;
    });
    afterAll(() => {
        delete global.FormData;
        delete global.localStorage;
    });
    beforeEach(() => {
        jest.clearAllMocks();
        apiRequest.post.mockResolvedValue({ data: {} });
    });

    test('sends ISIC codes, not their titles', () => {
        const formData = {
            isic4: [
                {
                    value: 'class:1410',
                    label: 'Manufacture of wearing apparel, except fur apparel',
                },
                { value: 'division:13', label: 'Manufacture of textiles' },
            ],
            isic5: [
                {
                    value: 'class:1410',
                    label: 'Manufacture of wearing apparel, except fur apparel',
                },
            ],
        };

        expect(submittedValues(formData, 'isic_4')).toEqual([
            'class:1410',
            'division:13',
        ]);
        apiRequest.post.mockClear();
        expect(submittedValues(formData, 'isic_5')).toEqual(['class:1410']);
    });

    test('still sends labels for the other select fields', () => {
        const formData = {
            sectors: [{ value: 'Apparel', label: 'Apparel' }],
        };

        expect(submittedValues(formData, 'sectors')).toEqual(['Apparel']);
    });
});

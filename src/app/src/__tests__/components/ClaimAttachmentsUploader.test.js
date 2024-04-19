import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import configureStore from 'redux-mock-store';
import { Provider } from 'react-redux';
import ClaimAttachmentsUploader from '../../components/ClaimAttachmentsUploader';
import { store } from '../../configureStore';

class File {
    constructor(parts, name, options) {
        this.parts = parts;
        this.name = name;
        this.options = options;
    }
}

global.File = File;

const mockStore = configureStore();

// Refer to this thread before testing mocked state - https://github.com/reduxjs/redux-mock-store/issues/71
describe('ClaimAttachmentsUploader', () => {
    let initialState;

    beforeEach(() => {
        initialState = mockStore({
            claimFacility: {
                claimData: {
                    formData: {
                        uploadFiles: [
                            new File(['file contents'], 'attachment_1.jpg', { type: 'image/jpg' })
                        ]
                    },
                },
            },
        });
    })


    global.URL.createObjectURL = jest.fn();

    it('renders without crashing', () => {
        render(<ClaimAttachmentsUploader uploadFiles={[]} updateUploadFiles={() => {}} store={initialState} />);
    });

    it('adds files when selected', () => {
        const { getByTestId } = render(
            <Provider store={initialState}>
                <ClaimAttachmentsUploader/>
            </Provider>
        );
        const file = new File(['file contents'], 'attachment_2.png', { type: 'image/png' });
        const fileList = { 0: file, length: 1, item: () => file };
        const fileInputField = getByTestId('claim-attachments-uploader-input');
        fireEvent.change(fileInputField, { target: { files: fileList } });
        const actions = initialState.getActions();

        // Test changes in real application store given action data we triggered
        store.dispatch({
            type: actions[0].type,
            payload: actions[0].payload,
            error: false
        })

        const updatedUploadFiles = store.getState().claimFacility.claimData.formData.uploadFiles
        expect(updatedUploadFiles.length).toBe(2)
    });

    /*
    it('removes files when clicked', async () => {
        const handleRemoveFile = jest.fn()

        const { getByLabelText } = render(
            <Provider store={initialState}>
                <ClaimAttachmentsUploader handleRemoveFile={handleRemoveFile} />
            </Provider>)

        fireEvent.click(getByLabelText('Remove'));
        const actions = initialState.getActions();
        console.log('actions are ', actions)
    });
    */

    /*
    it('displays error message for unsupported file format', () => {
        const { getByTestId } = render(<ClaimAttachmentsUploader uploadFiles={[]} updateUploadFiles={() => {}} store={initialState} />);
        const fileInputField = getByTestId('claim-attachments-uploader');
        fireEvent.drop(fileInputField, { dataTransfer: { files: [new File(['file contents'], 'file.txt', { type: 'text/plain' })] } });
        expect(getByText('file.txt could not be uploaded because it is not in a supported format.')).toBeInTheDocument();
    });

    it('displays error message for files exceeding the maximum size', () => {
        const { getByTestId } = render(<ClaimAttachmentsUploader uploadFiles={[]} updateUploadFiles={() => {}} store={initialState} />);
        const fileInputField = getByTestId('claim-attachments-uploader');
        const largeFile = new File(['file contents'], 'largefile.txt', { type: 'text/plain', size: 6 * 1024 * 1024 }); // 6MB file
        fireEvent.drop(fileInputField, { dataTransfer: { files: [largeFile] } });
        expect(getByText('largefile.txt could not be uploaded because it exceeds the maximum file size of 5MB.')).toBeInTheDocument();
    });

    it('displays error message for exceeding the maximum number of files', () => {
        const { getByTestId, getByText } = render(<ClaimAttachmentsUploader uploadFiles={[...Array(10).keys()].map(i => ({ name: `file${i}.txt` }))} updateUploadFiles={() => {}}  store={initialState} />);
        const fileInputField = getByTestId('claim-attachments-uploader');
        const newFile = new File(['file contents'], 'newfile.txt', { type: 'text/plain' });
        fireEvent.drop(fileInputField, { dataTransfer: { files: [newFile] } });
        expect(getByText('newfile.txt could not be uploaded because there is a maximum of 10 attachments and you have already uploaded 10 attachments.')).toBeInTheDocument();
    });
    */
});

import React from 'react';
import { fireEvent } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimAttachmentsUploader from '../../components/ClaimAttachmentsUploader';
import { updateClaimAFacilityUploadFiles } from '../../actions/claimFacility';

class File {
    constructor(parts, name, options) {
        this.parts = parts;
        this.name = name;
        this.options = options;
        this.size = options.size || 0;
    }
}

global.File = File;

describe('ClaimAttachmentsUploader', () => {
    global.URL.createObjectURL = jest.fn();

    it('renders without crashing', () => {
        renderWithProviders(
            <ClaimAttachmentsUploader inputId="files" title="Test" files={[]} updateUploadFiles={() => {}}/>
        )
    });

    it('adds files by action', () => {
        const {reduxStore} = renderWithProviders(
            <ClaimAttachmentsUploader inputId="files" title="Test" files={[]} updateUploadFiles={() => {}}/>
        )

        reduxStore.dispatch(
            updateClaimAFacilityUploadFiles([new File(['file contents'], 'attachment_1.jpg', { type: 'image/jpg' })])
        )

        const updatedUploadFiles = reduxStore.getState().claimFacility.claimData.formData.uploadFiles
        expect(updatedUploadFiles.length).toBe(1)
    });

    it('removes files by action', async () => {
        const {reduxStore} = renderWithProviders(
            <ClaimAttachmentsUploader inputId="files" title="Test" files={[]} updateUploadFiles={() => {}}/>
        )

        reduxStore.dispatch(
            updateClaimAFacilityUploadFiles([new File(['file contents'], 'attachment_1.jpg', { type: 'image/jpg' })])
        )

        const updatedUploadFilesFirst = reduxStore.getState().claimFacility.claimData.formData.uploadFiles
        expect(updatedUploadFilesFirst.length).toBe(1)

        reduxStore.dispatch(
            updateClaimAFacilityUploadFiles([])
        )

        const updatedUploadFilesSecond = reduxStore.getState().claimFacility.claimData.formData.uploadFiles
        expect(updatedUploadFilesSecond.length).toBe(0)
    });

    it('displays error message for unsupported file format', () => {
        const { getByTestId, getByText } = renderWithProviders(
            <ClaimAttachmentsUploader inputId="files" title="Test" files={[]} updateUploadFiles={() => {}}/>
        )
        const fileInputField = getByTestId('claim-attachments-uploader-input');
        fireEvent.drop(fileInputField, { dataTransfer: { files: [new File(['file contents'], 'attachment.txt', { type: 'text/plain' })] } });
        expect(getByText('attachment.txt could not be uploaded because it is not in a supported format.')).toBeInTheDocument();
    });

    it('displays error message for files exceeding the maximum size', () => {
        const { getByTestId, getByText } = renderWithProviders(
            <ClaimAttachmentsUploader inputId="files" title="Test" files={[]} updateUploadFiles={() => {}}/>
        )
        const fileInputField = getByTestId('claim-attachments-uploader-input');
        const largeFile = new File(['file contents'], 'attachment_large.jpg', { type: 'image/jpg', size: 6 * 1024 * 1024 }); // 6MB file
        fireEvent.drop(fileInputField, { dataTransfer: { files: [largeFile] } });
        expect(getByText('attachment_large.jpg could not be uploaded because it exceeds the maximum file size of 5MB.')).toBeInTheDocument();
    });

    it('displays error message for exceeding the maximum number of files', async () => {
        const { getByTestId, getByText } = renderWithProviders(
            <ClaimAttachmentsUploader inputId="files" title="Test" files={[...Array(10).keys()].map(i => ({ name: `attachment_${i}.png` }))} updateUploadFiles={() => {}}/>
        )
        const fileInputField = getByTestId('claim-attachments-uploader-input');
        fireEvent.drop(fileInputField, { dataTransfer: { files: [new File(['file contents'], 'attachment_11.jpg', { type: 'image/jpg' })] } });

        expect(getByText('attachment_11.jpg could not be uploaded because there is a maximum of 10 attachments and you have already uploaded 10 attachments.')).toBeInTheDocument();
    });
});

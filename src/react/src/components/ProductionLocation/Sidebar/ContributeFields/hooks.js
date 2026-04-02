import { useState } from 'react';

const useReportStatusDialog = () => {
    const [showDialog, setShowDialog] = useState(false);

    const openDialog = () => setShowDialog(true);
    const closeDialog = () => setShowDialog(false);

    return [showDialog, openDialog, closeDialog];
};

export default useReportStatusDialog;

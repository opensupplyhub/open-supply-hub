import { useState, useCallback } from 'react';

const useReportStatusDialog = () => {
    const [showDialog, setShowDialog] = useState(false);

    const openDialog = useCallback(() => {
        setShowDialog(true);
    }, []);

    const closeDialog = useCallback(() => {
        setShowDialog(false);
    }, []);

    return [showDialog, openDialog, closeDialog];
};

export default useReportStatusDialog;

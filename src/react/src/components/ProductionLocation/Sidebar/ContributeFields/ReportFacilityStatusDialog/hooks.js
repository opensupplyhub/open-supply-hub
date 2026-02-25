import { useState, useCallback } from 'react';

const useReportReason = () => {
    const [reason, setReason] = useState('');

    const resetReason = useCallback(() => {
        setReason('');
    }, []);

    return [reason, setReason, resetReason];
};

export default useReportReason;

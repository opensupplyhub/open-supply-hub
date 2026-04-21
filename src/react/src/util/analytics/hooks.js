import { useSelector } from 'react-redux';

const useViewerUserIdForAnalytics = () =>
    useSelector(state => {
        const id = state?.auth?.user?.user?.id;
        return id != null ? String(id) : null;
    });

export default useViewerUserIdForAnalytics;

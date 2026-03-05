import getIconURL from '../../components/ProductionLocation/Sidebar/NavBar/utils';
import env from '../../util/env';

jest.mock('../../util/env');

describe('getIconURL', () => {
    afterEach(() => {
        jest.resetAllMocks();
    });

    test('replaces "minio" with "localhost" when environment is local', () => {
        env.mockReturnValue('local');

        expect(getIconURL('http://minio:9000/icons/icon.png')).toBe(
            'http://localhost:9000/icons/icon.png',
        );
    });

    test('only replaces the first occurrence of "minio"', () => {
        env.mockReturnValue('local');

        expect(getIconURL('http://minio:9000/minio-bucket/icon.png')).toBe(
            'http://localhost:9000/minio-bucket/icon.png',
        );
    });

    test('returns the original URL when environment is not local', () => {
        env.mockReturnValue('production');

        const url = 'http://minio:9000/icons/icon.png';
        expect(getIconURL(url)).toBe(url);
    });

    test('returns the original URL when environment is undefined', () => {
        env.mockReturnValue(undefined);

        const url = 'http://minio:9000/icons/icon.png';
        expect(getIconURL(url)).toBe(url);
    });

    test('returns the URL unchanged in local env if it contains no "minio"', () => {
        env.mockReturnValue('local');

        const url = 'http://cdn.example.com/icons/icon.png';
        expect(getIconURL(url)).toBe(url);
    });

    test('calls env with "ENVIRONMENT"', () => {
        env.mockReturnValue('local');

        getIconURL('http://minio:9000/icons/icon.png');

        expect(env).toHaveBeenCalledWith('ENVIRONMENT');
    });
});

import React from 'react';
import { render, screen } from '@testing-library/react';

import ProfileVisibilityNote from '../../components/Shared/ProfileVisibilityNote/ProfileVisibilityNote';

describe('ProfileVisibilityNote', () => {
    it('says the value is shown on the profile', () => {
        render(<ProfileVisibilityNote isPubliclyVisible />);

        expect(screen.getByText('Shown on profile')).toBeInTheDocument();
    });

    it('says the value is not shown on the profile', () => {
        render(<ProfileVisibilityNote isPubliclyVisible={false} />);

        expect(screen.getByText('Not shown on profile')).toBeInTheDocument();
    });

    it('defaults to not shown', () => {
        render(<ProfileVisibilityNote />);

        expect(screen.getByText('Not shown on profile')).toBeInTheDocument();
    });
});

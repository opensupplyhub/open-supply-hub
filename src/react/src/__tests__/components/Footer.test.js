import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import Footer from './../../components/Footer/Footer';

test('Footer component', () => {
    render(
        <Router>
            <Footer />
        </Router>
    );

    const footer = screen.getByTestId('footer');
    expect(footer).toBeInTheDocument();

    // Footer links
    const donateLink = screen.getByText('Donate');
    expect(donateLink).toHaveAttribute('href', 'https://givebutter.com/opensupplyhub2022');

    const subscribeLink = screen.getByText('Subscribe');
    expect(subscribeLink).toHaveAttribute('href', 'https://share.hsforms.com/1bQwXClZUTjihXk3wt1SX2Abujql');

    const faqLink = screen.getByText('FAQs');
    expect(faqLink).toHaveAttribute('href', 'https://info.opensupplyhub.org/faqs');

    const carrerLink = screen.getByText("Careers")
    expect(carrerLink).toHaveAttribute('href', 'https://info.opensupplyhub.org/work-with-us')

    const blogLink = screen.getByText("Blog")
    expect(blogLink).toHaveAttribute('href', 'https://blog.opensupplyhub.org')

    const privacyPolicyLink = screen.getByText('Privacy Policy');
    expect(privacyPolicyLink).toHaveAttribute('href', 'https://info.opensupplyhub.org/privacy-policy');

    const mediaHubLink = screen.getByText('Media Hub');
    expect(mediaHubLink).toHaveAttribute('href', 'https://info.opensupplyhub.org/media-hub');

    const termsOfServiceLink = screen.getByText('Terms of Service');
    expect(termsOfServiceLink).toHaveAttribute('href', 'https://info.opensupplyhub.org/terms-of-service');

    const reportingLineLink = screen.getByText('Reporting Line');
    expect(reportingLineLink).toHaveAttribute('href', 'https://opensupplyhub.allvoices.co/');

    const contactUsLink = screen.getByText('Contact Us');
    expect(contactUsLink).toHaveAttribute('href', 'https://info.opensupplyhub.org/contact-us');

    // Social media links
    const linkedinLink = screen.getByText('LinkedIn');
    expect(linkedinLink.parentElement).toHaveAttribute('href', 'https://www.linkedin.com/company/open-supply-hub/');

    const youtubeLink = screen.getByText('YouTube');
    expect(youtubeLink.parentElement).toHaveAttribute('href', 'https://www.youtube.com/channel/UCy-66mcBwX2wlUM6kvKUrGw');

    const githubLink = screen.getByText('Github');
    expect(githubLink.parentElement).toHaveAttribute('href', 'https://github.com/opensupplyhub/open-supply-hub');
});

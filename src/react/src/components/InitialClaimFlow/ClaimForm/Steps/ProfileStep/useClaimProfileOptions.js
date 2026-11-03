import { useEffect, useState } from 'react';
import apiRequest from '../../../../../util/apiRequest';
import { makeGetClaimProfileOptionsURL } from '../../../../../util/util';

const toSelectOptions = names =>
    (Array.isArray(names) ? names : []).map(name => ({
        value: name,
        label: name,
    }));

const EMPTY_OPTIONS = Object.freeze({
    affiliations: [],
    certifications: [],
});

/*
 * The Affiliations and Certifications/Standards/Regulations options the
 * claim form offers. They are managed in the Django admin and served by
 * GET /api/claim-profile-options/ as plain names, which are also the
 * values stored on the claim, so each option's value and label are the
 * same string.
 *
 * Both fields are optional, so if the request fails the dropdowns stay
 * empty rather than blocking the step.
 */
const useClaimProfileOptions = () => {
    const [options, setOptions] = useState(EMPTY_OPTIONS);

    useEffect(() => {
        let isCancelled = false;

        apiRequest
            .get(makeGetClaimProfileOptionsURL())
            .then(({ data }) => {
                if (isCancelled) {
                    return;
                }
                setOptions({
                    affiliations: toSelectOptions(data?.affiliations),
                    certifications: toSelectOptions(data?.certifications),
                });
            })
            .catch(() => {});

        return () => {
            isCancelled = true;
        };
    }, []);

    return options;
};

export default useClaimProfileOptions;

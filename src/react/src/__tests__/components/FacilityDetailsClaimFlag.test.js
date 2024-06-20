import React from "react";
import { BrowserRouter as Router } from 'react-router-dom';
import { render, screen } from "@testing-library/react";
import FacilityDetailsClaimFlag from "../../components/FacilityDetailsClaimFlag"

describe('FacilityDetailsClaimFlag', () => {
    test('it renders without rashing', () => {
        const osId = "id_221kjaksiie";
        const isClaimed = true;
        const isPending = false;
        const isEmbed = false;

        render(
            <Router>
                <FacilityDetailsClaimFlag osId={osId} isClaimed={isClaimed} isPending={isPending} isEmbed={isEmbed} />
            </Router>
        )

        const banner = screen.getByTestId("cliam-banner")

        expect(banner).toBeInTheDocument()
    })

    test('facility has been claimed', () => {
        const osId = "id_221kjaksiie";
        const isClaimed = true;
        const isPending = false;
        const isEmbed = false;
        const text = 'This production location has been claimed by an owner or manager';

        render(
            <Router>
                <FacilityDetailsClaimFlag osId={osId} isClaimed={isClaimed} isPending={isPending} isEmbed={isEmbed} />
            </Router>
        )

        const banner = screen.getByTestId("cliam-banner")

        expect(banner).toHaveTextContent(text)
    })

    test('facility has not been claimed', () => {
        const osId = "id_221kjaksiie";
        const isClaimed = false;
        const isPending = false;
        const isEmbed = false;
        const text = 'This production location has not been claimed';

        render(
            <Router>
                <FacilityDetailsClaimFlag osId={osId} isClaimed={isClaimed} isPending={isPending} isEmbed={isEmbed} />
            </Router>
        )

        const banner = screen.getByTestId("cliam-banner")

        expect(banner).toHaveTextContent(text)
    })

    test('pending claim for facility ', () => {
        const osId = "id_221kjaksiie";
        const isClaimed = false;
        const isPending = true;
        const isEmbed = false;
        const text = 'There is a pending claim for this production location';

        render(
            <Router>
                <FacilityDetailsClaimFlag osId={osId} isClaimed={isClaimed} isPending={isPending} isEmbed={isEmbed} />
            </Router>
        )

        const banner = screen.getByTestId("cliam-banner")

        expect(banner).toHaveTextContent(text)
    })

    test('facility claim shoud not be rendered', () => {
        const osId = "id_221kjaksiie";
        const isClaimed = false;
        const isPending = true;
        const isEmbed = true;

        render(
            <Router>
                <FacilityDetailsClaimFlag osId={osId} isClaimed={isClaimed} isPending={isPending} isEmbed={isEmbed} />
            </Router>
        )

        const banner = screen.queryByTestId("cliam-banner")

        expect(banner).not.toBeInTheDocument()
    })


})

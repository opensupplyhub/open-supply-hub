import React from "react";
import renderWithProviders from "../../util/testUtils/renderWithProviders";
import ConfirmNotFoundLocationDialog from "../../components/Contribute/ConfirmNotFoundLocationDialog";
import history from "../../util/history";
import { contributeProductionLocationRoute, productionLocationInfoRoute } from "../../util/constants";

jest.mock("../../util/history", () => ({
    push: jest.fn(),
}));

const mockHandleConfirmDialogClose = jest.fn();
const mockClearLocations = jest.fn();

describe("ConfirmNotFoundLocationDialog component", () => {
    const defaultProps = {
        confirmDialogIsOpen: true,
        handleConfirmDialogClose: mockHandleConfirmDialogClose,
        clearLocations: mockClearLocations,
    };

    afterEach(() => {
        jest.clearAllMocks();
    });

    test("renders the dialog with the correct title and buttons", () => {
        const { getByText, getByRole } = renderWithProviders(
            <ConfirmNotFoundLocationDialog {...defaultProps} />,
        );

        expect(
            getByText(
                /Are you sure you have reviewed the entire list and could not find the production location?/i,
            ),
        ).toBeInTheDocument();
        expect(
            getByRole("button", {
                name: /No, I would like to try searching again/i,
            }),
        ).toBeInTheDocument();
        expect(
            getByRole("button", {
                name: /Yes, add a new production location/i,
            }),
        ).toBeInTheDocument();
        expect(getByRole("button", { name: /Close/i })).toBeInTheDocument();
    });

    test('calls handleSearchAgain when "No, I would like to try searching again" button is clicked', () => {
        const { getByRole } = renderWithProviders(
            <ConfirmNotFoundLocationDialog {...defaultProps} />,
        );
        const button = getByRole("button", {
            name: /No, I would like to try searching again/i,
        });
        button.click();

        expect(mockHandleConfirmDialogClose).toHaveBeenCalledTimes(1);
        expect(mockClearLocations).toHaveBeenCalledTimes(1);
        expect(history.push).toHaveBeenCalledWith(
            `${contributeProductionLocationRoute}?tab=name-address`,
        );
    });

    test('calls handleAddNewLocation when "Yes, add a new production location" button is clicked', () => {
        const { getByRole } = renderWithProviders(
            <ConfirmNotFoundLocationDialog {...defaultProps} />,
        );
        const button = getByRole("button", {
            name: /Yes, add a new production location/i,
        });
        button.click();

        expect(mockHandleConfirmDialogClose).toHaveBeenCalledTimes(1);
        expect(mockClearLocations).toHaveBeenCalledTimes(1);
        expect(history.push).toHaveBeenCalledWith(
            productionLocationInfoRoute,
        );
    });

    test("closes the dialog when the close button is clicked", () => {
        const { getByRole } = renderWithProviders(
            <ConfirmNotFoundLocationDialog {...defaultProps} />,
        );
        const button = getByRole("button", { name: /Close/i });
        button.click();

        expect(mockHandleConfirmDialogClose).toHaveBeenCalledTimes(1);
    });

    test("does not render the dialog when confirmDialogIsOpen is false", () => {
        const { queryByText } = renderWithProviders(
            <ConfirmNotFoundLocationDialog
                {...defaultProps}
                confirmDialogIsOpen={false}
            />,
        );

        expect(
            queryByText(
                /Are you sure you have reviewed the entire list and could not find the production location?/i,
            ),
        ).not.toBeInTheDocument();
    });
});

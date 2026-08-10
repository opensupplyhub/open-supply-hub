import {
    isFacilityProcessingNodeSelected,
    removeFacilityProcessingNodeById,
    toggleFacilityProcessingNode,
} from '../../components/Filters/HierarchicalTaxonomySearch/utils';
import { getFacilityProcessingSearchIndex } from '../../data/facilityProcessingSearchIndex';

const makeOption = value => ({ value, label: value });

describe('HierarchicalTaxonomySearch utils', () => {
    const { groups } = getFacilityProcessingSearchIndex();
    const textileGroup = groups.find(
        group =>
            group.facilityNode.label === 'Textile or Material Production',
    );
    const facilityNode = textileGroup.facilityNode;
    const materialCreationNode = textileGroup.processingNodes.find(
        node => node.label === 'Material Creation',
    );
    const materialProductionNode = textileGroup.processingNodes.find(
        node => node.label === 'Material Production',
    );

    test('parent deselect removes selected processing-type children', () => {
        const facilityType = [makeOption(facilityNode.label)];
        const processingType = [
            makeOption(materialCreationNode.label),
            makeOption(materialProductionNode.label),
        ];

        const nextSelection = toggleFacilityProcessingNode(
            facilityNode,
            facilityType,
            processingType,
        );

        expect(nextSelection.facilityType).toEqual([]);
        expect(nextSelection.processingType).toEqual([]);
    });

    test('removeFacilityProcessingNodeById clears facility type and its children', () => {
        const facilityType = [makeOption(facilityNode.label)];
        const processingType = [
            makeOption(materialCreationNode.label),
            makeOption(materialProductionNode.label),
        ];

        const nextSelection = removeFacilityProcessingNodeById(
            facilityNode.id,
            facilityType,
            processingType,
        );

        expect(nextSelection.facilityType).toEqual([]);
        expect(nextSelection.processingType).toEqual([]);
    });

    test('isFacilityProcessingNodeSelected reflects facility and processing selections', () => {
        expect(
            isFacilityProcessingNodeSelected(facilityNode, [], []),
        ).toBe(false);
        expect(
            isFacilityProcessingNodeSelected(
                facilityNode,
                [makeOption(facilityNode.label)],
                [],
            ),
        ).toBe(true);
        expect(
            isFacilityProcessingNodeSelected(
                materialCreationNode,
                [],
                [makeOption(materialCreationNode.label)],
            ),
        ).toBe(true);
    });
});

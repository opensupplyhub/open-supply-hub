const RELATIONSHIP_OPTIONS = [
    { value: 'owner', label: 'I am the owner of this production location' },
    {
        value: 'manager',
        label: 'I am a manager working at this production location',
    },
    {
        value: 'parent_company_owner_or_manager',
        label: 'I represent the parent company that owns/manages this facility',
    },
    {
        value: 'worker',
        label:
            "I work here but don't have management authority (will require supervisor verification)",
    },
    {
        value: 'partner',
        label: 'I am a buyer, supplier, agent, or other business partner',
    },
    {
        value: 'other',
        label: 'Other relationship',
    },
];

export default RELATIONSHIP_OPTIONS;

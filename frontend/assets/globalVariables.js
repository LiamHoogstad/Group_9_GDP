// genres
export const unsortedGenres = [
    { value: 'Pop', label: 'Pop' },
    { value: 'Jazz', label: 'Jazz' },
    { value: 'Funk', label: 'Funk' },
    { value: 'Folk', label: 'Folk' },
    { value: 'Disco', label: 'Disco' },
    { value: 'House', label: 'House' },
    { value: 'Techno', label: 'Techno' },
    { value: 'Alternative Hip Hop', label: 'Alternative Hip Hop' },
    { value: 'Hip Hop', label: 'Hip Hop' },
    { value: 'Rap', label: 'Rap' },
    ];

export const genres = unsortedGenres.sort((a, b) => a.label.localeCompare(b.label));

// instruments
export const unsortedInstruments = [
    { value: 'Guitar', label: 'Guitar' },
    { value: 'Vocal', label: 'Vocal' },
    { value: 'Drums', label: 'Drums' },
    { value: 'Synth', label: 'Synth' },
    { value: 'Violin', label: 'Violin' },
    { value: 'Brass', label: 'Brass' },
    { value: 'Wind Instruments', label: 'Wind Instruments' },
    { value: 'Piano', label: 'Piano' },
  ];
  
export const instruments = unsortedInstruments.sort((a, b) => a.label.localeCompare(b.label));

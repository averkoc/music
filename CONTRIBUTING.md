# Contributing to MuseScore to SWAM Workflow

Thank you for your interest in contributing! This project aims to make expressive virtual instrument performance accessible to music composers.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, MuseScore version)
- Sample MIDI file if possible

### Suggesting Features

Feature requests are welcome! Please include:
- Use case description
- Why this would be useful
- Proposed implementation (if you have ideas)

### Code Contributions

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow PEP 8 style guidelines
   - Add type hints to function signatures
   - Include docstrings for new functions
   - Comment complex MIDI processing logic

4. **Test your changes**
   - Test with various MIDI files
   - Verify with both violin and saxophone
   - Check that existing functionality still works

5. **Commit with clear messages**
   ```bash
   git commit -m "Add support for SWAM Cello"
   ```

6. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/musescore-to-swam.git
cd musescore-to-swam

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run scripts in development
cd scripts
python process_midi.py --help
```

## Code Style

- **Python**: Follow PEP 8
- **Line length**: Max 100 characters
- **Type hints**: Use for all function parameters and returns
- **Docstrings**: Google style for functions and classes

### Example:

```python
def process_velocity(velocity: int, instrument: SWAMInstrument) -> List[mido.Message]:
    """
    Convert note velocity to SWAM CC messages.
    
    Args:
        velocity: MIDI velocity (0-127)
        instrument: Target SWAM instrument
        
    Returns:
        List of MIDI control change messages
    """
    # Implementation...
```

## Testing

Before submitting a PR:

1. **Manual testing**
   ```bash
   python process_midi.py test.mid -i violin -v
   ```

2. **Code formatting**
   ```bash
   black scripts/
   ```

3. **Linting**
   ```bash
   flake8 scripts/
   ```

## Priority Areas for Contribution

### High Priority
- [ ] Add more SWAM instruments (cello, trumpet, flute)
- [ ] Improve articulation detection algorithms
- [ ] Real-time MIDI processing mode
- [ ] GUI application for non-coders

### Medium Priority
- [ ] Unit tests for CC mapper
- [ ] More sophisticated crescendo/diminuendo handling
- [ ] Export CameloPro presets programmatically
- [ ] Integration with music21 for analysis

### Low Priority
- [ ] Support for Kontakt libraries
- [ ] VST3 parameter automation export
- [ ] Web-based MIDI processor
- [ ] Machine learning for expression prediction

## Documentation

When adding features, please update:
- `README.md` if it affects main workflow
- `docs/workflow_guide.md` for detailed procedures
- `scripts/README.md` for new scripts
- Inline code comments for complex logic

## Questions?

Feel free to open an issue with the "question" label, or reach out to the maintainers.

## Code of Conduct

Be respectful and constructive. We're all here to make music software better!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

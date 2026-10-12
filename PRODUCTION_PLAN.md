# Gilgamesh Datadisk Production Plan

## Overview

This document outlines the complete production plan for the Gilgamesh datadisk, including asset creation workflows, responsibilities, timelines, and deliverables.

## 📊 Current State

### ✅ Completed
- **Content Structure**: All YAML files created and validated
  - 21 places (Uruk locations + Mesopotamian architecture)
  - 16 NPCs (8 epic characters + 8 historical figures)
  - 16 dialogues (branching conversation trees)
  - 8 quests (complete epic questline)
  - 18+ lore entries
  - Full English and Czech translations (500+ keys each)
  
- **Technical Infrastructure**:
  - `datadisk.yaml` manifest
  - Validation passing
  - `Makefile` for development
  - Debian packaging files
  - Voice synthesis configuration

- **Asset Infrastructure**:
  - Placeholder portraits generated (19)
  - Placeholder textures generated
  - `tools/blender/` - Blender Python scripts
  - `tools/generate_assets.py` - Asset generation script
  - `research/HISTORICAL_REFERENCES.md` - Comprehensive historical research
  - `3D_MODELS.md` - Detailed model specifications
  - `ASSET_GENERATION.md` - Complete asset creation guide

### 🎯 Remaining
1. **Real Artwork** (High Priority)
   - 19 character portraits
   - Cover image
   - 6 music tracks
   
2. **3D Models** (Medium Priority)
   - 13 architectural models
   - 8 character models
   - 3 monster models
   
3. **Testing** (Essential)
   - Local testing with server
   - Client integration testing
   - Performance testing

## 🎯 Production Phases

### Phase 1: Content Finalization (Week 1-2)
**Status**: ✅ COMPLETE

**Deliverables**:
- [x] All YAML content created
- [x] All translations complete
- [x] Validation passing
- [x] Placeholder assets generated
- [x] Historical research compiled
- [x] Modeling specifications created
- [x] Blender scripts created
- [x] Asset generation scripts created

**Tasks**:
- Review and finalize all content
- Verify historical accuracy
- Polish translations
- Optimize quest flow

**Timeline**: 2 weeks (Completed)

---

### Phase 2: Asset Creation (Week 3-6)
**Status**: 🟡 IN PROGRESS (Infrastructure Ready)

**Deliverables**:
- [ ] 19 character portraits (512x512)
- [ ] Cover image (1024x768)
- [ ] 6 music tracks (OGG)
- [ ] 24 3D models (GLB)

#### Subphase 2.1: Portraits (Week 3)
**Priority**: High
**Responsible**: Artist / AI Assistant

**Tasks**:
- Generate or create 19 character portraits
- Ensure historical accuracy
- Maintain consistent style
- Optimize file sizes (< 1 MiB each)

**Method Options**:
1. **AI Generation** (Recommended)
   - Use `make prompts` to generate AI prompts
   - Use Stable Diffusion, Midjourney, or DALL-E
   - Expected time: 2-4 hours with AI
   
2. **Manual Creation**
   - Use reference images from historical sources
   - Create in GIMP, Krita, or Photoshop
   - Expected time: 3-5 days

**Checklist**:
- [ ] Gilgamesh
- [ ] Enkidu
- [ ] Ishtar
- [ ] Shamhat
- [ ] Humbaba
- [ ] Utnapishtim
- [ ] Ur-Shanabi
- [ ] Scorpion Man
- [ ] Ninsun
- [ ] Anu
- [ ] Bull of Heaven
- [ ] High Priest of Anu
- [ ] High Priestess of Ishtar
- [ ] Temple Scribe
- [ ] Royal Guard
- [ ] Uruk Noble
- [ ] Uruk Merchant
- [ ] Potter
- [ ] Weaver

**Validation**:
```bash
# Check all portraits exist
ls -1 media/portraits/*.jpg | wc -l  # Should be 19
```

#### Subphase 2.2: 3D Models (Week 4-5)
**Priority**: High
**Responsible**: 3D Artist

**Tasks**:
- Create architectural models using Blender scripts
- Create character models
- Ensure historical accuracy
- Optimize for performance

**Method Options**:
1. **Blender Scripts** (Recommended)
   - Run `make models` to generate basic geometry
   - Enhance manually for production quality
   - Expected time: 2-3 weeks
   
2. **Manual Modeling**
   - Use specifications from `3D_MODELS.md`
   - Model from scratch in Blender
   - Expected time: 3-4 weeks

**Priority Order**:
1. **Essential Models** (Week 4)
   - Ziggurat of Uruk
   - Gilgamesh
   - Enkidu
   
2. **High Priority Models** (Week 5)
   - Ziggurat of Anu
   - Ziggurat of Ishtar
   - White Temple
   - Uruk Wall Section
   - Ishtar
   - Shamhat
   - Humbaba
   
3. **Medium Priority Models** (Week 5-6)
   - Remaining architecture
   - Remaining characters
   - Monsters

**Validation**:
```bash
# Check all models exist
find media/models -name "*.glb" | wc -l  # Should be 24
```

#### Subphase 2.3: Music (Week 4-5)
**Priority**: Medium
**Responsible**: Sound Designer / Researcher

**Tasks**:
- Find or create 6 music tracks
- Convert to OGG format
- Ensure seamless looping
- Optimize file sizes (< 8 MiB each)

**Method Options**:
1. **Free Music Sources** (Recommended)
   - Free Music Archive
   - Incompetech (Kevin MacLeod)
   - Tabletop Audio
   - Expected time: 1-2 days
   
2. **AI Generation**
   - Use AI music generators
   - Expected time: 1 day
   
3. **Original Composition**
   - Create custom music
   - Expected time: 2-3 weeks

**Tracks Needed**:
- [ ] temple.ogg
- [ ] ishtar_shrine.ogg
- [ ] cedar_forest.ogg
- [ ] mountain_echo.ogg
- [ ] waters_of_death.ogg
- [ ] utnapishtim.ogg

**Validation**:
```bash
# Check all music files exist
ls -1 media/music/*.ogg | wc -l  # Should be 6
```

#### Subphase 2.4: Cover Image (Week 4)
**Priority**: High
**Responsible**: Artist

**Tasks**:
- Create cover image using prompt
- Ensure eye-catching design
- Include main characters and landmarks

**Method Options**:
1. **AI Generation** (Recommended)
   - Use cover prompt from `prompts/cover_prompt.json`
   - Expected time: 1-2 hours
   
2. **Manual Creation**
   - Create in image editing software
   - Expected time: 1-2 days

**Validation**:
```bash
# Check cover exists
ls -1 media/cover/cover.jpg | wc -l  # Should be 1
```

---

### Phase 3: Integration and Testing (Week 7)
**Status**: ⏳ NOT STARTED

**Deliverables**:
- [ ] All assets integrated
- [ ] Local testing complete
- [ ] Performance validated
- [ ] Bug fixes applied

**Tasks**:
1. **Asset Integration**
   - Copy all assets to correct locations
   - Update references if needed
   - Run validation
   
2. **Local Testing**
   - Stage for testing: `make stage`
   - Start server: `make server`
   - Test in client
   - Verify all portraits display
   - Verify all models render
   - Verify all music plays
   - Test all quests
   - Test all dialogues
   
3. **Performance Testing**
   - Test with multiple players
   - Check FPS with 3D models
   - Optimize if needed
   
4. **Bug Fixes**
   - Fix any issues found
   - Revalidate after fixes

**Validation**:
```bash
# Validate complete datadisk
make check

# Test locally
make stage
make server
# Test in client
```

---

### Phase 4: Packaging and Release (Week 8)
**Status**: ⏳ NOT STARTED

**Deliverables**:
- [ ] Debian package built
- [ ] Documentation complete
- [ ] Release notes written

**Tasks**:
1. **Package Building**
   - Update version in `debian/changelog`
   - Update version in `datadisk.yaml`
   - Build package: `dpkg-buildpackage -us -uc -b`
   - Test installation
   
2. **Documentation**
   - Update README with final info
   - Add release notes
   - Update screenshots
   
3. **Final Validation**
   - Full validation
   - Install test
   - Final playtest

**Validation**:
```bash
# Build package
cd ishtaria-datadisk-gilgamesh
dpkg-buildpackage -us -uc -b

# Install package
sudo dpkg -i ../ishtaria-datadisk-gilgamesh_*.deb

# Verify installation
ls /usr/share/ishtaria/datadisks/gilgamesh/
```

## 📋 Resource Requirements

### Human Resources
1. **Project Lead** (1 person)
   - Coordinates all activities
   - Ensures historical accuracy
   - Manages timeline
   
2. **Artist** (1 person)
   - Creates portraits
   - Creates cover image
   - Ensures visual consistency
   - Expected time: 3-5 days
   
3. **3D Artist** (1 person)
   - Creates 3D models
   - Optimizes for performance
   - Expected time: 2-3 weeks
   
4. **Sound Designer** (1 person, optional)
   - Sources or creates music
   - Expected time: 1-2 days
   
5. **QA Tester** (1 person)
   - Tests all content
   - Reports bugs
   - Expected time: 3-5 days

### Software Requirements
1. **Blender 3.0+** - For 3D modeling
2. **AI Image Generator** - For portrait creation (optional)
   - Stable Diffusion
   - Midjourney
   - DALL-E
3. **Image Editor** - For manual portrait creation (optional)
   - GIMP
   - Krita
   - Photoshop
4. **Audio Editor** - For music editing (optional)
   - Audacity
   - Ardour
5. **FFmpeg** - For audio conversion
6. **Python 3** - For asset generation scripts
7. **Piper TTS** - For voice synthesis (optional)

## 💰 Budget Estimate

### Option 1: Volunteer/Internal Team
- **Cost**: $0 (using free tools and volunteer time)
- **Time**: 6-8 weeks
- **Quality**: Variable (depends on team skills)

### Option 2: Commissioned Art
- **Portraits**: 19 x $50 = $950
- **3D Models**: 24 x $100 = $2,400
- **Music**: 6 x $50 = $300
- **Cover**: $100
- **Total**: ~$3,750
- **Time**: 4-6 weeks

### Option 3: AI-Assisted (Recommended)
- **AI Subscription**: $20-50/month
- **Manual Touchup**: 40 hours @ $25/hour = $1,000
- **Total**: ~$1,050
- **Time**: 4-5 weeks
- **Quality**: High

### Option 4: Mixed Approach
- **AI Portraits**: $0-50
- **Manual 3D Models**: 10 critical models x $100 = $1,000
- **Free Music**: $0
- **Manual Cover**: $100
- **Total**: ~$1,150
- **Time**: 4-5 weeks
- **Quality**: High for critical assets, AI for others

## 📅 Timeline

| Week | Phase | Tasks | Deliverables |
|------|-------|-------|--------------|
| 1-2 | Content Finalization | ✅ Completed | All YAML, translations, infrastructure |
| 3 | Portrait Creation | Generate/create 19 portraits | 19 portrait files |
| 4 | Cover + Music Start | Create cover, start music, start 3D | Cover, 3-4 portraits, 2-3 models |
| 5 | 3D Focus | Continue 3D models, finish music | 15-18 models, all music |
| 6 | 3D Completion | Finish all 3D models | All 24 models |
| 7 | Integration & Testing | Integrate assets, test thoroughly | Fully tested datadisk |
| 8 | Packaging & Release | Build package, finalize docs | Release package |

## ✅ Quality Assurance Checklist

### Content Quality
- [ ] All text historically accurate
- [ ] All translations verified
- [ ] All references exist and are valid
- [ ] Quest flow logical and tested
- [ ] Dialogues engaging and branching

### Asset Quality
- [ ] Portraits match character descriptions
- [ ] Portraits historically accurate
- [ ] Portraits consistent style
- [ ] 3D models match specifications
- [ ] 3D models historically accurate
- [ ] 3D models optimized for performance
- [ ] Music appropriate for locations
- [ ] Music loops seamlessly
- [ ] Cover image eye-catching

### Technical Quality
- [ ] All files validate
- [ ] All references resolved
- [ ] File sizes within limits
- [ ] File formats correct
- [ ] No broken links
- [ ] No missing files

### Testing Quality
- [ ] Server starts without errors
- [ ] Datadisk appears in world generation
- [ ] All locations generate correctly
- [ ] All NPCs appear at designated places
- [ ] All dialogues work
- [ ] All quests progress correctly
- [ ] All lore accessible
- [ ] All portraits display
- [ ] All music plays
- [ ] All models render
- [ ] Performance acceptable

## 📊 Metrics

### File Counts
- YAML files: 40+
- Portrait files: 19
- Music files: 6
- 3D model files: 24
- Total files: ~90

### Content Statistics
- Places: 21
- NPCs: 16
- Dialogues: 16
- Quests: 8
- Lore entries: 18+
- Translation keys: 500+ (per language)
- Voice lines: 100+

### Asset Statistics
- Portrait total size: < 19 MiB
- Music total size: < 48 MiB
- Model total size: < 96 MiB
- Total package size: < 170 MiB

## 🎯 Risk Mitigation

### Risk 1: Historical Inaccuracy
**Mitigation**:
- Use `research/HISTORICAL_REFERENCES.md` as primary source
- Consult academic sources
- Have expert review if possible
- Document sources for all content

### Risk 2: Asset Creation Delays
**Mitigation**:
- Start with placeholder assets (already done)
- Use AI generation for rapid prototyping
- Prioritize essential assets first
- Have backup manual creation methods

### Risk 3: Performance Issues
**Mitigation**:
- Create LOD versions for large models
- Optimize polycounts
- Test with target hardware
- Create simplified versions if needed

### Risk 4: Integration Problems
**Mitigation**:
- Test incrementally
- Validate after each asset addition
- Use staging environment
- Document integration steps

## 📝 Communication Plan

### Weekly Meetings
- Review progress
- Address blockers
- Adjust timeline if needed

### Daily Updates
- Slack/Discord channel for quick questions
- Git commits with descriptive messages

### Milestone Reviews
- End of each phase
- Demonstrate deliverables
- Get stakeholder feedback

## 📚 Training Resources

### For Artists
- `research/HISTORICAL_REFERENCES.md` - Historical accuracy guide
- `ASSET_GENERATION.md` - Asset creation guide
- `tools/generate_assets.py` - Prompt generator

### For 3D Artists
- `3D_MODELS.md` - Complete model specifications
- `tools/blender/README.md` - Blender script documentation
- `tools/blender/*.py` - Blender scripts

### For Testers
- `NEXT_STEPS.md` - Testing procedures
- `Makefile` - Development commands
- `README.md` - Datadisk documentation

## 🎉 Success Criteria

The Gilgamesh datadisk will be considered **successful** when:

1. ✅ **Content Complete**
   - All YAML content created and validated
   - All translations complete
   
2. ✅ **Assets Complete**
   - All 19 portraits created
   - Cover image created
   - All 6 music tracks added
   - At least essential 3D models created (5+)
   
3. ✅ **Functional**
   - Validation passes without errors
   - All content loads in server
   - All quests can be completed
   - All dialogues work
   
4. ✅ **Immersive**
   - Portraits enhance character experience
   - 3D models enhance location experience
   - Music enhances atmosphere
   
5. ✅ **Historically Accurate**
   - Content based on Epic of Gilgamesh
   - Artwork based on archaeological evidence
   - Architecture based on historical reconstructions
   
6. ✅ **Performant**
   - Runs smoothly on target hardware
   - Loads quickly
   - No performance degradation

7. ✅ **Packaged**
   - Debian package builds successfully
   - Installs without errors
   - Works in production environment

## 📅 Current Status Update

**As of**: 2026-10-10

**Phase**: Phase 1 (Content Finalization) - ✅ **COMPLETE**

**Phase 2 Progress**: 
- Infrastructure: ✅ 100% (All scripts and tools created)
- Portraits: ❌ 0% (Waiting for asset creation)
- 3D Models: ❌ 0% (Waiting for asset creation)
- Music: ❌ 0% (Waiting for asset creation)
- Cover: ❌ 0% (Waiting for asset creation)

**Next Actions**:
1. Generate prompts: `make prompts`
2. Use prompts with AI or create manually
3. Run Blender scripts: `make models`
4. Enhance generated models
5. Add music tracks

**Blockers**:
- None (all infrastructure in place)

**Resources Ready**:
- ✅ Historical research complete
- ✅ Blender scripts created
- ✅ AI prompts ready
- ✅ Asset organization defined
- ✅ Validation working
- ✅ Documentation complete

## 🎯 Immediate Next Steps

To move to Phase 2 (Asset Creation):

1. **Run these commands**:
   ```bash
   cd /home/vitex/Projects/Ishtaria/ishtaria-datadisk-gilgamesh
   make prompts
   ```
   This generates all the prompts needed for AI image generation.

2. **For Portraits**:
   - Use the prompts in `prompts/portrait_prompts.json`
   - Generate images using your preferred AI tool
   - Save to `media/portraits/[character].jpg`

3. **For 3D Models**:
   - Run: `make models` (requires Blender)
   - OR manually run Blender scripts from `tools/blender/`
   - Enhance the generated models
   - Export to `media/models/[category]/[model].glb`

4. **For Music**:
   - Download appropriate tracks from free sources
   - Convert to OGG: `ffmpeg -i input.mp3 -c:a libvorbis -q:a 6 output.ogg`
   - Save to `media/music/[track].ogg`

5. **For Cover**:
   - Use prompt from `prompts/cover_prompt.json`
   - Generate or create manually
   - Save to `media/cover/cover.jpg`

6. **Validate**:
   ```bash
   make check
   ```

## 📞 Support

If you encounter issues during production:

1. **Validation Errors**
   - Check `ishtaria-protocol/tests/validate_datadisk.py`
   - Ensure all referenced files exist
   - Verify file formats and sizes

2. **Blender Issues**
   - Check Blender version (3.0+ required)
   - Verify Python version
   - Review `tools/blender/README.md`

3. **Asset Issues**
   - Review `ASSET_GENERATION.md`
   - Check file organization
   - Verify naming conventions

4. **Content Issues**
   - Review `research/HISTORICAL_REFERENCES.md`
   - Consult primary sources
   - Ask for feedback from team

---

**This production plan provides a clear path from the current state (structurally complete with placeholders) to a production-ready Gilgamesh datadisk with all custom assets.**

The infrastructure is now in place. The remaining work is asset creation, which can be done using the provided scripts, prompts, and documentation.

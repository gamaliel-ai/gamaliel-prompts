# User Profiles

This directory contains user profile files that shape how Gamaliel adapts its responses to different audiences. Each profile represents a specific type of user based on their spiritual background, biblical knowledge, and learning needs.

## What is a User Profile?

A user profile is a YAML configuration that defines:
- **User characteristics** (spiritual background, experience level)
- **Response adaptation** (language complexity, depth of explanation)
- **Learning approach** (how to present biblical concepts)
- **Example questions** (typical inquiries from this user type)

Profiles help Gamaliel tailor responses to be appropriate and helpful for users at different stages of their spiritual journey.

## How Profiles Work

### User Experience Levels

Profiles are organized by experience level (0-5):
- **0-1**: Beginners and seekers (no or limited biblical knowledge)
- **2-3**: Growing in faith (some biblical familiarity)
- **4-5**: Mature believers (extensive biblical knowledge)

### Response Adaptation

Profiles influence:
- **Language complexity** - Simple vs. theological terminology
- **Explanation depth** - Basic concepts vs. advanced interpretation
- **Biblical references** - Few vs. extensive cross-references
- **Application focus** - Practical vs. theological emphasis

### Integration with the System

- **User Selection**: Users choose a profile that matches their background
- **Response Shaping**: The AI adapts language, depth, and approach
- **Question Suggestions**: Profile influences suggested follow-up questions
- **Theology Compatibility**: Profiles work with any theological perspective

### Christian Identity and Theology Selection

The `is_christian` field determines whether users can select their theological perspective:

- **`is_christian: true`**: Users who identify as Christian can choose from available theological perspectives (Reformed, Catholic, Lutheran, etc.)
- **`is_christian: false`**: Non-Christian users receive responses using the default theology, as they wouldn't have a specific Christian theological preference

## Current Profiles

### Beginners & Seekers (Levels 0-2)

- **`curious_explorer.yml`** (Level 0) - Never read the Bible, curious about faith
- **`universal_explorer.yml`** (Level 1) - Exploring life's big questions, open to biblical wisdom
- **`spiritual_seeker.yml`** (Level 2) - Read some Bible, exploring Christianity specifically

### Growing Believers (Levels 3-4)

- **`new_believer.yml`** (Level 3) - Recently committed to Jesus, learning to read Bible regularly
- **`growing_christian.yml`** (Level 4) - Reads Bible regularly, wants deeper understanding

### Mature Believers (Level 5)

- **`mature_believer.yml`** (Level 5) - Studies Bible daily, seeks advanced theological insights

## Profile Structure

```yaml
name: "Profile Name"
description: "Brief description of the user type"
is_christian: true/false  # Whether the target user identifies as Christian
experience_level: 0-5
instructions: |
  Detailed instructions for adapting responses to this user type:
  
  - Language and terminology preferences
  - Depth of biblical explanation
  - Approach to theological concepts
  - Focus areas and emphases
  - How to handle questions and doubts

example_questions:
  - "Typical question from this user type"
  - "Another common question"
  - "Questions that show their level of understanding"
```

## Profile Guidelines

### What to Include

1. **Clear User Definition**
   - Specific spiritual background and experience level
   - Typical questions and concerns
   - Learning needs and preferences

2. **Response Adaptation Guidelines**
   - How to adjust language complexity
   - Depth of biblical explanation
   - Approach to theological concepts
   - Handling of doubts and questions

3. **Example Questions**
   - Representative questions from this user type
   - Questions that demonstrate their knowledge level
   - Common concerns and interests

### Quality Standards

1. **User-Centered Design**
   - Focus on user needs and experience
   - Clear, actionable guidance for response adaptation
   - Respectful of user's spiritual journey

2. **Comprehensive Coverage**
   - Address language, depth, and approach
   - Include practical guidance for common scenarios
   - Provide clear examples

3. **Consistent Structure**
   - Follow established YAML format
   - Maintain consistent terminology
   - Clear organization of instructions

## Limited Profile Set

We maintain a **limited, curated set of profiles** rather than trying to cover every possible user type. This approach:

### Benefits
- **Quality over quantity** - Each profile is carefully crafted
- **Clear user paths** - Users can easily identify their profile
- **Maintainable** - Easier to keep profiles current and accurate
- **Consistent experience** - Predictable adaptation across the system

### Profile Selection Criteria
- **Broad applicability** - Serves many users, not just edge cases
- **Clear differentiation** - Distinct from other profiles
- **Proven usefulness** - Addresses real user needs
- **Spiritual journey alignment** - Fits natural progression of faith

## Editing Existing Profiles

### Guidelines for Changes

1. **User-Focused Improvements**
   - Enhance clarity of user definition
   - Improve response adaptation guidance
   - Add relevant example questions

2. **Maintain Coverage**
   - Ensure all experience levels are represented
   - Keep profiles distinct and complementary
   - Preserve user journey progression

3. **Test Effectiveness**
   - Verify changes improve user experience
   - Ensure compatibility with theological perspectives
   - Check for unintended consequences

### Review Process

1. **User Experience Review**
   - Does this better serve the target user type?
   - Are the adaptations clear and actionable?
   - Do example questions represent real user needs?

2. **System Integration Review**
   - Compatible with all theological perspectives?
   - Works well with the response generation system?
   - Maintains consistency with other profiles?

3. **Community Feedback**
   - Gather input from users in this category
   - Test with real questions and scenarios
   - Iterate based on feedback

## Adding New Profiles

New profiles are **rarely added** and only when:

1. **Clear Gap Exists**
   - Significant user type not covered by existing profiles
   - Evidence of user need for additional profile

2. **Distinct User Type**
   - Clearly different from existing profiles
   - Requires different response adaptation approach

3. **Broad Applicability**
   - Serves substantial user population
   - Not just a niche or edge case

### Proposal Process

1. **Identify Need**
   - Document the user type and their needs
   - Show why existing profiles don't serve them well
   - Provide evidence of user demand

2. **Draft Profile**
   - Create complete YAML file following structure
   - Include comprehensive instructions and examples
   - Test with representative questions

3. **Community Review**
   - Submit for community feedback
   - Test with target user group
   - Iterate based on input

## Contributing

### For Existing Profiles
1. **Identify improvement** - What would better serve users?
2. **Propose specific changes** - Clear, actionable modifications
3. **Test effectiveness** - Verify improvements work as intended
4. **Submit pull request** - Include rationale and testing results

### For New Profiles
1. **Demonstrate need** - Show clear gap in current coverage
2. **Create complete profile** - Full YAML file with all required elements
3. **Test thoroughly** - Verify it serves target users effectively
4. **Submit for review** - Include evidence of need and effectiveness

## Resources

- [Main README](../README.md) - Overview of the project
- [CONTRIBUTING.md](../CONTRIBUTING.md) - General contribution guidelines
- [Theologies README](../theologies/README.md) - How profiles work with theological perspectives

---

*The goal is to provide appropriate, helpful responses for users at every stage of their spiritual journey.* 
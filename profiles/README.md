# User Profiles

This directory contains Bible familiarity profiles. Each profile is a rung on a four-step ladder that calibrates how much explanation, navigation help, and study-tool depth Gamaliel includes. Profiles describe how well someone already knows their way around the text. They are not faith-stage, maturity, or academic-credential labels.

## What is a User Profile?

A user profile is a YAML configuration that defines:

- **Bible familiarity** (how much of the text they already know their way around)
- **Response adaptation** (language complexity, depth of explanation)
- **Learning approach** (how to present biblical concepts)
- **Example questions** (typical inquiries from this familiarity level)

## How Profiles Work

### Familiarity ladder (levels 1–4)

- **1**: New to the Bible (little reading; few verses; does not yet know where to begin)
- **2**: Basic familiarity (some stories, verses, or characters; not yet at home finding things in the Bible)
- **3**: Read regularly (can find books; some context for most passages) — default Ask behavior when unset
- **4**: Study in depth (narrative structure; cross-references, commentaries, and study tools). This is study practice, not seminary training.

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

Bible familiarity is independent of Christian tradition. All four rungs set `is_christian: true` so tradition selection is not gated on the familiarity ladder. Tradition is a separate control.

## Current Profiles

- **`new_to_the_bible.yml`** (Level 1) — Little reading; explain people, books, and terms
- **`basic_familiarity.yml`** (Level 2) — Knows some stories and names; still needs help finding things in the text
- **`read_regularly.yml`** (Level 3) — Can find books; default when the user has not chosen a level
- **`study_in_depth.yml`** (Level 4) — Narrative structure, cross-references, commentaries, and study tools

## Profile Structure

```yaml
name: 'Profile Name'
description: 'Brief description of the user type'
is_christian: true/false # Compatibility field; not used to gate tradition
experience_level: 1-4
instructions: |
  Detailed instructions for adapting responses to this user type:

  - Language and terminology preferences
  - Depth of biblical explanation
  - Approach to theological concepts
  - Focus areas and emphases
  - How to handle questions and doubts

example_questions:
  - 'Typical question from this user type'
  - 'Another common question'
  - 'Questions that show their level of understanding'
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

As the project matures, we will welcome contributions to improve user profiles. See [CONTRIBUTING.md](../CONTRIBUTING.md) for general contribution guidelines.

## Resources

- [Main README](../README.md) - Overview of the project
- [Theologies README](../theologies/README.md) - How profiles work with theological perspectives

---

_The goal is to provide appropriate, helpful responses for users at every stage of their spiritual journey._

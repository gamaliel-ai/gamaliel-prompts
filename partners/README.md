# Partner Subdomains

> **⚠️ Note: Early Development Stage**
>
> Partner subdomains are currently in early development. We expect changes to the partner system as we refine our approach. We will begin actively onboarding new partners once the system matures and stabilizes.

This directory contains partner configuration files that enable organizations to create their own branded subdomain of Gamaliel. Partners can provide their audience with a customized Bible study experience while maintaining the core theological integrity and transparency of the Gamaliel system.

## What is a Partner Subdomain?

A partner subdomain is a customized version of Gamaliel that:

- **Bears your organization's branding** (logo, messaging)
- **Targets your specific audience** (custom instructions and example questions)
- **Maintains full transparency** (all prompts and guidelines remain open source)
- **Provides your own URL** (e.g., `your-org.gamaliel.ai`)

Partners include churches, ministries, nonprofits, Bible study groups, and other organizations that want to provide their community with trustworthy, AI-powered Bible study.

## How Partner Subdomains Work

### Technical Implementation

1. **Subdomain Routing**: `your-org.gamaliel.ai` routes to the main Gamaliel application
2. **Partner Detection**: The system detects the subdomain and loads your partner configuration
3. **Custom Branding**: Your logo, colors, and messaging are displayed
4. **Audience Adaptation**: Responses are tailored to your specific audience
5. **Full Transparency**: All prompts, guidelines, and responses remain auditable

### What Partners Can Customize

- **Visual Branding**: Logo, icon, colors, and styling
- **Audience Targeting**: Custom instructions for your specific users
- **Example Questions**: Questions relevant to your community
- **About Information**: Your organization's story and mission (markdown)
- **Theological Perspective**: Choose from available theological guidelines

### Christian Identity and Theology Selection

The `is_christian` field determines whether your audience can select their theological perspective:

- **`is_christian: true`**: If your audience identifies as Christian, they can choose from available theological perspectives (Reformed, Catholic, Lutheran, etc.)
- **`is_christian: false`**: If your audience includes non-Christians, they will receive responses using the default theology, as they wouldn't have a specific Christian theological preference

### What Remains Consistent

- **Core Theological Guidelines**: All responses maintain essential Christian orthodoxy
- **Biblical Authority**: Scripture remains the primary source of truth
- **Transparency**: All prompts and responses are open for review
- **Privacy**: No user data collection or tracking
- **Quality**: Same high-quality biblical interpretation and response generation

## Creating Your Partner Subdomain

### Step 1: Prepare Your Organization Information

Gather the following information about your organization:

#### Basic Information

- **Organization name** and brief description
- **Target audience** (who you serve and their needs)
- **Mission and values** (what drives your work)
- **Website URL** and contact information

#### Visual Assets

- **Logo** (SVG or high-resolution PNG, ideally with transparent background)
- **Icon** (square format, 512x512px recommended)
- **Brand colors** (if you want to customize the interface)

#### Audience Understanding

- **Primary user type** (experience level, spiritual background)
- **Common questions** your audience asks
- **Specific challenges** they face
- **How you want to help** them through Scripture

### Step 2: Create Your Partner Configuration

Create a YAML file following this structure:

```yaml
slug: 'your-organization'
name: 'Your Organization Name'
description: 'Brief description of your audience and mission'
is_christian: true/false # Whether your target audience identifies as Christian

instructions: |
  Detailed instructions for how Gamaliel should adapt responses for your audience:

  - Who your audience is and what they're dealing with
  - How to approach biblical questions for your community
  - Language and tone preferences
  - Areas of emphasis or special focus
  - How to connect Scripture to your audience's specific needs

partner:
  logo_url: 'https://your-domain.com/logo.svg'
  icon_url: 'https://your-domain.com/icon.png'
  website: 'https://your-organization.org'
  description: 'Brief description for the interface'
  about_text: |
    # Your Organization's Story

    [Your organization's mission, values, and how you help people]

    ## Why We Partnered with Gamaliel

    [Explain why you chose to provide biblical study resources]

    ## How Gamaliel Can Help

    [How your audience can benefit from exploring Scripture]

example_questions:
  - 'Question your audience commonly asks'
  - 'Another typical question from your community'
  - "Questions that reflect your audience's needs and concerns"
```

### Step 3: Submit Your Configuration

1. **Fork the repository** and create a feature branch
2. **Add your partner file** to the `partners/` directory
3. **Test your configuration** locally if possible
4. **Submit a pull request** with:
   - Your partner configuration file
   - Brief description of your organization and audience
   - Any special requirements or considerations

### Step 4: Review and Launch

1. **Theological Review**: We'll verify your configuration aligns with core guidelines
2. **Technical Review**: We'll test the integration and branding
3. **Launch**: Once approved, your subdomain will be activated
4. **Promotion**: We'll help you announce your partnership

## Partner Configuration Guidelines

### Required Elements

1. **Clear Audience Definition**

   - Specific description of who you serve
   - Their spiritual background and experience level
   - Common questions and concerns

2. **Appropriate Instructions**

   - How to adapt responses for your audience
   - Language and tone preferences
   - Areas of emphasis or special focus

3. **Relevant Example Questions**

   - Questions your audience actually asks
   - Topics relevant to your mission
   - Issues your community faces

4. **Professional Branding**
   - High-quality logo and icon
   - Clear organization description
   - Professional about text

### Quality Standards

1. **Audience-Focused**

   - Instructions clearly serve your specific audience
   - Example questions reflect real user needs
   - Approach matches your organization's values

2. **Theologically Sound**

   - Compatible with core Christian guidelines
   - Respectful of biblical authority
   - Aligns with your organization's beliefs

3. **Professional Presentation**
   - Clear, well-written content
   - High-quality visual assets
   - Consistent with your organization's brand

### What to Avoid

1. **Generic Content**

   - Instructions that could apply to any organization
   - Example questions that aren't specific to your audience
   - Vague or unclear descriptions

2. **Theological Conflicts**

   - Instructions that contradict core guidelines
   - Approaches that deny essential Christian doctrines
   - Content that undermines biblical authority

3. **Poor Quality Assets**
   - Low-resolution or inappropriate logos
   - Broken or inaccessible URLs
   - Unprofessional or unclear content

## Partner Benefits

### For Your Organization

- **Extend Your Ministry**: Provide biblical resources 24/7
- **Reach New Audiences**: Serve people who might not visit your website
- **Maintain Your Brand**: Customized experience with your branding
- **No Technical Overhead**: No hosting, maintenance, or development required
- **Full Transparency**: Your community can see exactly how responses are generated

### For Your Audience

- **Trusted Source**: Biblical study through your organization's lens
- **Always Available**: Access to Scripture study whenever they need it
- **Privacy-First**: No tracking, no accounts, no data collection
- **Theologically Sound**: Responses grounded in historic Christian orthodoxy
- **Relevant to Them**: Tailored to their specific needs and questions

## Partner Responsibilities

### What Partners Provide

1. **Clear Audience Definition**

   - Detailed understanding of who you serve
   - Common questions and concerns
   - Appropriate language and approach

2. **Quality Content**

   - Professional branding assets
   - Well-written organization information
   - Relevant example questions

3. **Ongoing Engagement**
   - Promote your subdomain to your community
   - Gather feedback from users
   - Suggest improvements based on usage

### What Gamaliel Provides

1. **Technical Infrastructure**

   - Subdomain hosting and routing
   - System maintenance and updates
   - Security and performance optimization

2. **Theological Integrity**

   - Core guidelines and biblical authority
   - Quality assurance and review
   - Ongoing theological oversight

3. **Support and Resources**
   - Documentation and guidance
   - Community and partnership support
   - Promotion and visibility

## Getting Started

### For Churches

- **Identify your congregation's needs** - What biblical questions do they have?
- **Consider your outreach goals** - How can this serve your community?
- **Prepare your branding** - Logo, colors, and messaging
- **Define your approach** - How do you want to present biblical truth?

### For Ministries

- **Clarify your mission** - Who do you serve and how?
- **Understand your audience** - What are their spiritual needs?
- **Align with your values** - How does this fit your ministry approach?
- **Plan your promotion** - How will you introduce this to your community?

### For Nonprofits

- **Define your service area** - What population do you serve?
- **Identify spiritual needs** - How can Scripture address their challenges?
- **Maintain your focus** - How does this complement your existing work?
- **Ensure accessibility** - How can you make this available to your community?

### For Bible Study Groups

- **Clarify your group's focus** - What topics or themes do you study?
- **Consider your members** - What are their experience levels and needs?
- **Plan for growth** - How can this help your group expand?
- **Maintain community** - How can this enhance your in-person gatherings?

## Support and Resources

- **Technical Support**: Help with configuration and integration
- **Theological Guidance**: Assistance with instructions and approach
- **Community**: Connect with other partners and share best practices
- **Documentation**: Comprehensive guides and examples

## Contact

As the partner system matures, we will begin onboarding new partners. For now, you can:

- **GitHub**: Submit an issue or pull request to express interest
- **Website**: [gamaliel.ai](https://gamaliel.ai) for general information

---

_Partner with Gamaliel to provide your community with trustworthy, transparent, and accessible Bible study resources._

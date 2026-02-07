# Project Examples for Cortex Government AI System

This directory contains example project configurations that demonstrate how to use the project wizard and configure different types of applications.

## Available Examples

### 1. Blog Platform (`blog-platform-config.json`)
**Project Type:** Next.js Blog Platform  
**Description:** A modern, SEO-optimized blog platform with content management and social sharing features.

**Key Features:**
- Next.js with TypeScript
- Responsive design with Tailwind CSS
- SEO optimization helpers
- Content management system integration
- Social sharing capabilities

**Use Cases:**
- Personal blog portfolios
- Company/organization blogs
- Content marketing sites
- Technical documentation sites

### 2. Firebook Cooking Platform (`firebook-config.json`)
**Project Type:** React Web Application  
**Description:** A comprehensive social cooking platform with AI recipe generation, meal planning, and community features.

**Key Features:**
- AI-powered recipe generation
- Social cooking sessions
- Meal planning calendar
- Dietary restriction support
- Shopping list integration
- User profiles and community features

**Use Cases:**
- Cooking apps and platforms
- Recipe sharing communities
- Meal planning services
- Social cooking networks

### 3. General Web Application (`general-webapp-config.json`)
**Project Type:** React/Next.js Full Stack  
**Description:** A flexible template for modern web applications with authentication, databases, and deployment ready features.

**Key Features:**
- User authentication system
- Database integration with Prisma
- RESTful API endpoints
- Responsive UI components
- Security and performance optimizations

**Use Cases:**
- SaaS applications
- E-commerce platforms
- Dashboard applications
- Enterprise web apps
- APIs and microservices

## Usage Instructions

### 1. Running the Wizard

```bash
# Run the wizard with interactive mode
python cortex_gov_wizard.py --interactive

# Run with specific configuration file
python cortex_gov_wizard.py --config examples/blog-platform-config.json

# Generate multiple projects
python cortex_gov_wizard.py --config examples/blog-platform-config.json --output ./generated-projects/blog-platform
```

### 2. Customizing Configurations

Each JSON configuration can be modified to fit your specific needs:

```json
{
  "project_name": "My Custom Project",
  "project_type": "react-nextjs",
  "description": "Description of your project",
  "epics": [...],
  "features": {...},
  "tech_stack": {...}
}
```

### 3. Validation

The wizard will automatically validate your configuration:

```bash
# Validate configuration without generating
python cortex_gov_wizard.py --validate --config examples/blog-platform-config.json
```

## File Structure

```
examples/
├── README.md                           # This documentation
├── blog-platform-config.json           # Blog platform configuration
├── firebook-config.json               # Cooking platform configuration
├── general-webapp-config.json          # General web app configuration
└── custom-template-config.json         # (Create your own)
```

## Testing Examples

To test the wizard with each example:

```bash
# Test blog platform configuration
python cortex_gov_wizard.py --non-interactive --config examples/blog-platform-config.json

# Test firebook configuration  
python cortex_gov_wizard.py --non-interactive --config examples/firebook-config.json

# Test general webapp configuration
python cortex_gov_wizard.py --non-interactive --config examples/general-webapp-config.json
```

## Creating Custom Examples

To create your own project configuration:

1. Copy one of the existing templates
2. Modify the `project_name`, `description`, and other fields
3. Adjust epics and tasks to match your project requirements
4. Add your specific features and tech stack
5. Test the configuration using the wizard

## Best Practices

1. **Start Simple**: Begin with a basic configuration and add complexity gradually
2. **Validate Early**: Use the `--validate` flag to check configurations before full generation
3. **Organize Epics**: Group related tasks into logical epics
4. **Prioritize Tasks**: Use P0, P1, P2 priority levels effectively
5. **Document Changes**: Keep this README updated with new examples

## Troubleshooting

### Common Issues

1. **Validation Errors**: Check JSON syntax and required fields
2. **Missing Dependencies**: Ensure all referenced tech stack items are valid
3. **Task Dependencies**: Verify that prerequisite tasks are properly ordered
4. **File Permissions**: Check write permissions for output directories

### Getting Help

- Check the main `PROJECT.md` for system documentation
- Review the wizard source code for configuration details
- Test with the simplest example first, then progress to more complex ones
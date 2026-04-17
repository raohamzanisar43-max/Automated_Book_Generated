# Automated Book Generation System - Frontend

A modern React frontend for the AI-powered automated book generation system.

## Features

- **Dashboard**: Overview of all books with status tracking
- **Book Creation**: Intuitive book creation with AI outline generation
- **Outline Management**: Review, edit, and approve book outlines
- **Chapter Generation**: Generate chapters with context chaining
- **Real-time Updates**: Live status updates and notifications
- **Export Options**: Export books in DOCX, PDF, and TXT formats
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

- **React 18** - Modern React with hooks
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **React Query** - Server state management
- **React Hook Form** - Form handling
- **Lucide React** - Beautiful icons
- **React Hot Toast** - Toast notifications

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- VS Code (recommended) with Tailwind CSS extension

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd kickstart/frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Install VS Code Extensions** (recommended):
   - Tailwind CSS IntelliSense
   - Prettier - Code formatter
   - ESLint

4. **Create environment file**:
```bash
cp .env.example .env
```

5. **Configure environment variables** in `.env`:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

6. **Start the development server**:
```bash
npm start
```

The app will be available at `http://localhost:3000`

## Tailwind CSS Setup

This project uses Tailwind CSS for styling. The configuration includes:

### Configuration Files
- `tailwind.config.js` - Tailwind configuration with custom colors and animations
- `postcss.config.js` - PostCSS configuration for Tailwind processing
- `.vscode/settings.json` - VS Code settings for optimal Tailwind experience

### Custom Components
The project includes custom Tailwind components defined in `src/index.css`:

- `.btn` - Base button styles
- `.btn-primary` - Primary button variant
- `.btn-secondary` - Secondary button variant
- `.btn-success` - Success button variant
- `.btn-danger` - Danger button variant
- `.card` - Card component styles
- `.input` - Form input styles
- `.status-badge` - Status badge styles
- `.loading-spinner` - Loading animation

### Custom Colors
- `primary` - Custom primary color palette (blue shades)
- Extended color palette for consistent theming

### Custom Animations
- `fade-in` - Fade in animation
- `slide-up` - Slide up animation
- `pulse-slow` - Slow pulse animation

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.jsx      # Main layout component
│   ├── LoadingSpinner.jsx
│   ├── StatusBadge.jsx
│   ├── CreateBook.jsx  # Book creation form
│   └── ChapterView.jsx # Chapter detail view
├── hooks/              # Custom React hooks
│   └── useBooks.js     # Book-related hooks
├── pages/              # Page components
│   ├── Dashboard.jsx   # Main dashboard
│   ├── BookDetail.jsx  # Book detail view
│   └── ChapterView.jsx # Chapter detail view
├── services/           # API services
│   └── api.js          # Axios configuration and API calls
├── App.jsx             # Main app component
├── index.css           # Tailwind CSS with custom components
└── index.jsx           # Entry point
```

## Available Scripts

- `npm start` - Runs the app in development mode with hot reload
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App (one-way operation)

## Key Features

### Book Management
- Create new books with AI-powered outline generation
- Track book status through the entire generation pipeline
- View and manage all books from the dashboard

### Outline Review
- Review AI-generated outlines
- Provide feedback for improvements
- Approve outlines to proceed to chapter generation

### Chapter Generation
- Generate chapters with context from previous chapters
- Review and regenerate individual chapters
- Track chapter generation progress

### Export Options
- Export completed books in multiple formats
- Download generated content instantly
- Share books with stakeholders

## API Integration

The frontend integrates with the FastAPI backend through RESTful APIs:

- `GET /books` - Fetch all books
- `POST /books` - Create new book
- `GET /books/{id}` - Get book details
- `PUT /books/{id}/outline` - Update outline
- `POST /books/{id}/regenerate-outline` - Regenerate outline
- `GET /books/{id}/chapters` - Get book chapters
- `POST /books/{id}/chapters/{number}` - Generate chapter
- `POST /books/{id}/export` - Export book

## State Management

The app uses React Query for server state management:
- Automatic caching and background updates
- Optimistic updates for better UX
- Error handling and retry logic
- Loading states and error boundaries

## Styling with Tailwind CSS

### Utility Classes
The app uses Tailwind's utility classes for rapid development:
- Responsive design with breakpoint prefixes
- Hover, focus, and active states
- Dark mode support (can be added)
- Custom component classes

### Custom Components
Custom component classes are defined using `@layer components`:
- Consistent design system
- Reusable styles
- Easy maintenance

### Responsive Design
Fully responsive design using Tailwind's responsive utilities:
- Mobile-first approach
- Tablet and desktop optimizations
- Flexible layouts

## Error Handling

- Global error boundaries catch unexpected errors
- API errors are handled with user-friendly messages
- Loading states provide feedback during operations
- Toast notifications for user actions

## Performance

- Code splitting for optimal loading
- Lazy loading of components
- Optimized re-renders with React.memo
- Efficient API calls with React Query
- PurgeCSS in production builds

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development Tips

### VS Code Setup
1. Install the recommended extensions
2. Enable Tailwind CSS IntelliSense
3. Configure Prettier for code formatting

### Styling Guidelines
- Use utility classes for most styling
- Create component classes for complex patterns
- Maintain consistent spacing and colors
- Use responsive prefixes for mobile design

### State Management
- Use React Query for server state
- Local state with useState for UI state
- Context API for global UI state if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Follow the coding standards
6. Submit a pull request

## Troubleshooting

### Tailwind CSS Issues
If you encounter Tailwind CSS linting errors:
1. Install the Tailwind CSS IntelliSense extension
2. Ensure VS Code settings are configured
3. Restart VS Code after installing extensions
4. Check that `tailwind.config.js` is properly configured

### Common Issues
- **Classes not applying**: Check that Tailwind is properly imported
- **Build errors**: Ensure all dependencies are installed
- **API errors**: Verify backend is running and accessible

## License

This project is licensed under the MIT License.

'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { 
  Bookmark, 
  Clock, 
  Heart, 
  MessageCircle, 
  Search, 
  TrendingUp,
  ArrowRight,
  Menu,
  X,
  Mail,
  Zap,
  Code2,
  FlaskConical,
  Rocket,
  Sparkles,
  ExternalLink
} from 'lucide-react'
import { useState } from 'react'
import Link from 'next/link'

// Tech news articles with DLL voice
const featuredPost = {
  id: 1,
  title: "AI is Writing Code Now. Are We Still the Authors?",
  excerpt: "Anthropic claims AI generates nearly all their code. The question isn't whether AI can code—it's what happens to the humans who used to. A meditation on creativity, automation, and staying curious.",
  category: "Curious Minds",
  readTime: "6 min read",
  date: "Feb 16, 2025",
  likes: 892,
  comments: 156,
  source: "Industry Watch"
}

const blogPosts = [
  {
    id: 2,
    title: "The $391B Question: Where Is AI Actually Going?",
    excerpt: "Everyone's betting big on AI. But between the hype and the hardware, what problems are we actually solving? A practical look at the AI landscape.",
    category: "Deep Dives",
    readTime: "8 min read",
    date: "Feb 15, 2025",
    likes: 567,
    comments: 89
  },
  {
    id: 3,
    title: "Agentic AI: By 2028, Your Boss Might Be an Algorithm",
    excerpt: "Gartner predicts 15% of work decisions will be autonomous by 2028. That's not dystopia—that's an opportunity to rethink what work means.",
    category: "Future Watch",
    readTime: "5 min read",
    date: "Feb 14, 2025",
    likes: 445,
    comments: 67
  },
  {
    id: 4,
    title: "Building Tools That Don't Suck: A Manifesto",
    excerpt: "Less enterprise. More energy. Why most software is boring and how we're trying to make things that spark joy instead of spreadsheets.",
    category: "Lab Notes",
    readTime: "7 min read",
    date: "Feb 13, 2025",
    likes: 723,
    comments: 94
  },
  {
    id: 5,
    title: "Open Source AI: The Plot Thickens",
    excerpt: "OpenAI's latest moves. The open source community's response. And why this matters for anyone building things on the internet.",
    category: "Curious Minds",
    readTime: "6 min read",
    date: "Feb 12, 2025",
    likes: 389,
    comments: 52
  }
]

const categories = [
  { name: "Curious Minds", count: 42, icon: Sparkles },
  { name: "Lab Notes", count: 28, icon: FlaskConical },
  { name: "Deep Dives", count: 35, icon: Code2 },
  { name: "Future Watch", count: 19, icon: Rocket },
  { name: "Ship Log", count: 24, icon: Zap }
]

const trendingTopics = [
  "AI Code Generation",
  "Indie Hacking",
  "Open Source Tools",
  "Creative Coding",
  "Future of Work"
]

// Ad configurations using uploaded images
const sidebarAds = [
  {
    id: 1,
    image: "/upload/dude.png",
    title: "The Dude Abides",
    subtitle: "Wisdom for the curious coder",
    cta: "Explore"
  },
  {
    id: 2,
    image: "/upload/dude-henge.png",
    title: "Built to Last",
    subtitle: "Architecture that stands up",
    cta: "Learn More"
  }
]

const inContentAds = [
  {
    id: 1,
    image: "/upload/dll-graffiti-01.png",
    title: "Street Cred. Digital Skills.",
    subtitle: "Where curiosity meets code",
    cta: "Join the Lab"
  },
  {
    id: 2,
    image: "/upload/dll-graffiti-02.png",
    title: "Make Something Cool",
    subtitle: "Experimental tools for curious builders",
    cta: "Start Building"
  }
]

export default function Home() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-3 group">
              <img 
                src="/upload/retro-dll-logo.png" 
                alt="DudeLogicLabs" 
                className="h-10 w-auto group-hover:scale-105 transition-transform"
              />
              <div className="hidden sm:block">
                <span className="font-bold text-xl tracking-tight">
                  DudeLogicLabs
                </span>
                <p className="text-xs text-muted-foreground -mt-0.5">Software for the Seriously Curious</p>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-6">
              <Link href="/" className="text-sm font-medium text-foreground hover:text-orange-500 transition-colors">Blog</Link>
              <Link href="/apps" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Apps</Link>
              <a href="#" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Shop</a>
              <a href="#" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">About</a>
            </nav>

            {/* Search & Actions */}
            <div className="flex items-center gap-3">
              <button className="p-2 rounded-full hover:bg-muted transition-colors">
                <Search className="w-5 h-5 text-muted-foreground" />
              </button>
              <Button className="hidden sm:flex bg-foreground text-background hover:bg-foreground/90 gap-2">
                <Mail className="w-4 h-4" />
                Stay Curious
              </Button>
              <button 
                className="md:hidden p-2 rounded-full hover:bg-muted transition-colors"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-border">
              <nav className="flex flex-col gap-3">
                <Link href="/" className="text-sm font-medium text-foreground py-2">Blog</Link>
                <Link href="/apps" className="text-sm font-medium text-muted-foreground py-2">Apps</Link>
                <a href="#" className="text-sm font-medium text-muted-foreground py-2">Shop</a>
                <a href="#" className="text-sm font-medium text-muted-foreground py-2">About</a>
                <Button className="mt-2 bg-foreground text-background hover:bg-foreground/90 gap-2">
                  <Mail className="w-4 h-4" />
                  Stay Curious
                </Button>
              </nav>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content Area */}
            <div className="lg:col-span-2 space-y-8">
              {/* Featured Post */}
              <Card className="overflow-hidden border-2 border-foreground/10 hover:border-foreground/20 transition-colors duration-300">
                <CardContent className="p-6 sm:p-8">
                  <div className="flex items-center gap-3 mb-4">
                    <Badge className="bg-foreground text-background border-0 font-medium">
                      Featured
                    </Badge>
                    <Badge variant="outline" className="text-xs font-medium">
                      {featuredPost.category}
                    </Badge>
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {featuredPost.readTime}
                    </span>
                  </div>
                  <h1 className="text-2xl sm:text-3xl font-bold mb-4 leading-tight hover:text-orange-500 transition-colors cursor-pointer">
                    {featuredPost.title}
                  </h1>
                  <p className="text-muted-foreground mb-6 leading-relaxed text-lg">
                    {featuredPost.excerpt}
                  </p>
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-500 to-red-500 flex items-center justify-center text-white font-bold text-sm">
                        DLL
                      </div>
                      <div>
                        <p className="text-sm font-medium">DudeLogicLabs</p>
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <ExternalLink className="w-3 h-3" />
                          {featuredPost.source}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-muted-foreground">
                      <span className="text-xs">{featuredPost.date}</span>
                      <button className="flex items-center gap-1 text-sm hover:text-foreground transition-colors">
                        <Heart className="w-4 h-4" />
                        <span className="hidden sm:inline">{featuredPost.likes}</span>
                      </button>
                      <button className="flex items-center gap-1 text-sm hover:text-foreground transition-colors">
                        <MessageCircle className="w-4 h-4" />
                        <span className="hidden sm:inline">{featuredPost.comments}</span>
                      </button>
                      <button className="hover:text-foreground transition-colors">
                        <Bookmark className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* In-Content Ad 1 */}
              <Card className="overflow-hidden border border-dashed border-foreground/30 bg-gradient-to-r from-zinc-900 to-slate-900">
                <CardContent className="p-0">
                  <div className="flex flex-col sm:flex-row">
                    <div className="sm:w-2/5 h-48 sm:h-auto overflow-hidden">
                      <img 
                        src={inContentAds[0].image} 
                        alt={inContentAds[0].title}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="p-6 sm:w-3/5 flex flex-col justify-center">
                      <p className="text-xs text-zinc-400 uppercase tracking-wider mb-2">From the Lab</p>
                      <h3 className="text-white font-bold text-xl mb-2">{inContentAds[0].title}</h3>
                      <p className="text-zinc-300 text-sm mb-4">{inContentAds[0].subtitle}</p>
                      <Button className="w-fit bg-white text-zinc-900 hover:bg-zinc-100">
                        {inContentAds[0].cta}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Blog Posts Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {blogPosts.slice(0, 2).map((post) => (
                  <Card key={post.id} className="overflow-hidden group border-2 border-transparent hover:border-foreground/10 transition-all duration-300 hover:shadow-lg">
                    <CardContent className="p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <Badge variant="outline" className="text-xs font-medium">
                          {post.category}
                        </Badge>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {post.readTime}
                        </span>
                      </div>
                      <h2 className="font-bold text-lg mb-2 leading-snug group-hover:text-orange-500 transition-colors cursor-pointer">
                        {post.title}
                      </h2>
                      <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
                        {post.excerpt}
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">{post.date}</span>
                        <div className="flex items-center gap-3 text-muted-foreground">
                          <button className="flex items-center gap-1 text-xs hover:text-foreground transition-colors">
                            <Heart className="w-3.5 h-3.5" />
                            {post.likes}
                          </button>
                          <button className="flex items-center gap-1 text-xs hover:text-foreground transition-colors">
                            <MessageCircle className="w-3.5 h-3.5" />
                            {post.comments}
                          </button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* In-Content Ad 2 */}
              <Card className="overflow-hidden border border-dashed border-foreground/30 bg-gradient-to-r from-slate-900 to-zinc-900">
                <CardContent className="p-0">
                  <div className="flex flex-col sm:flex-row-reverse">
                    <div className="sm:w-2/5 h-48 sm:h-auto overflow-hidden">
                      <img 
                        src={inContentAds[1].image} 
                        alt={inContentAds[1].title}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="p-6 sm:w-3/5 flex flex-col justify-center">
                      <p className="text-xs text-zinc-400 uppercase tracking-wider mb-2">Experimental</p>
                      <h3 className="text-white font-bold text-xl mb-2">{inContentAds[1].title}</h3>
                      <p className="text-zinc-300 text-sm mb-4">{inContentAds[1].subtitle}</p>
                      <Button className="w-fit bg-white text-zinc-900 hover:bg-zinc-100">
                        {inContentAds[1].cta}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* More Blog Posts */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {blogPosts.slice(2, 4).map((post) => (
                  <Card key={post.id} className="overflow-hidden group border-2 border-transparent hover:border-foreground/10 transition-all duration-300 hover:shadow-lg">
                    <CardContent className="p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <Badge variant="outline" className="text-xs font-medium">
                          {post.category}
                        </Badge>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {post.readTime}
                        </span>
                      </div>
                      <h2 className="font-bold text-lg mb-2 leading-snug group-hover:text-orange-500 transition-colors cursor-pointer">
                        {post.title}
                      </h2>
                      <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
                        {post.excerpt}
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">{post.date}</span>
                        <div className="flex items-center gap-3 text-muted-foreground">
                          <button className="flex items-center gap-1 text-xs hover:text-foreground transition-colors">
                            <Heart className="w-3.5 h-3.5" />
                            {post.likes}
                          </button>
                          <button className="flex items-center gap-1 text-xs hover:text-foreground transition-colors">
                            <MessageCircle className="w-3.5 h-3.5" />
                            {post.comments}
                          </button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Newsletter CTA */}
              <Card className="border-2 border-foreground/10 bg-gradient-to-br from-zinc-50 to-slate-50 dark:from-zinc-900 dark:to-slate-900">
                <CardContent className="p-6 relative z-10">
                  <div className="flex flex-col sm:flex-row items-center gap-6">
                    <img 
                      src="/upload/dude-dll-file.png" 
                      alt="DudeLogicLabs"
                      className="h-28 w-auto rounded-lg"
                    />
                    <div className="text-center sm:text-left flex-1">
                      <p className="text-xs uppercase tracking-wider mb-2 text-muted-foreground">Stay Curious</p>
                      <h3 className="font-bold text-xl mb-2">The Lab Report</h3>
                      <p className="text-muted-foreground mb-4">Weekly dispatches from the intersection of curiosity and code. No corporate speak.</p>
                      <div className="flex flex-col sm:flex-row gap-2 max-w-md mx-auto sm:mx-0">
                        <input 
                          type="email" 
                          placeholder="your@email.com"
                          className="flex-1 px-4 py-2 rounded-lg border border-foreground/20 bg-background focus:outline-none focus:border-foreground/40 text-sm"
                        />
                        <Button className="bg-foreground text-background hover:bg-foreground/90 gap-2">
                          <Mail className="w-4 h-4" />
                          Subscribe
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Load More */}
              <div className="flex justify-center pt-4">
                <Button variant="outline" className="gap-2 hover:bg-foreground hover:text-background transition-colors">
                  More Articles
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Sidebar */}
            <aside className="space-y-6">
              {/* About Card */}
              <Card className="border-2 border-foreground/10">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <img 
                      src="/upload/retro-dll-logo.png" 
                      alt="DLL" 
                      className="h-12 w-auto"
                    />
                    <div>
                      <h3 className="font-bold text-lg mb-1">DudeLogicLabs</h3>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        A tiny software studio shipping focused tools, lovable apps, and merch for the seriously curious.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Sidebar Ad 1 */}
              <Card className="overflow-hidden border border-dashed border-foreground/30">
                <CardContent className="p-0">
                  <div className="relative">
                    <img 
                      src={sidebarAds[0].image} 
                      alt={sidebarAds[0].title}
                      className="w-full h-52 object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent" />
                    <div className="absolute bottom-0 left-0 right-0 p-4">
                      <p className="text-xs text-zinc-300 uppercase tracking-wider mb-1">From the Shop</p>
                      <h4 className="font-bold text-white text-lg">{sidebarAds[0].title}</h4>
                      <p className="text-zinc-300 text-sm mb-3">{sidebarAds[0].subtitle}</p>
                      <Button size="sm" className="bg-white text-zinc-900 hover:bg-zinc-100">
                        {sidebarAds[0].cta}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Categories */}
              <Card className="border-2 border-foreground/10">
                <CardContent className="p-6">
                  <h3 className="font-bold text-lg mb-4">Explore</h3>
                  <div className="space-y-2">
                    {categories.map((category) => (
                      <a 
                        key={category.name}
                        href="#" 
                        className="flex items-center justify-between py-2.5 px-3 rounded-lg hover:bg-muted transition-colors group"
                      >
                        <div className="flex items-center gap-2">
                          <category.icon className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                          <span className="text-sm font-medium group-hover:text-foreground transition-colors">{category.name}</span>
                        </div>
                        <span className="text-xs text-muted-foreground">{category.count}</span>
                      </a>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Sidebar Ad 2 */}
              <Card className="overflow-hidden border border-dashed border-foreground/30">
                <CardContent className="p-0">
                  <div className="relative">
                    <img 
                      src={sidebarAds[1].image} 
                      alt={sidebarAds[1].title}
                      className="w-full h-52 object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent" />
                    <div className="absolute bottom-0 left-0 right-0 p-4">
                      <p className="text-xs text-zinc-300 uppercase tracking-wider mb-1">Featured</p>
                      <h4 className="font-bold text-white text-lg">{sidebarAds[1].title}</h4>
                      <p className="text-zinc-300 text-sm mb-3">{sidebarAds[1].subtitle}</p>
                      <Button size="sm" className="bg-white text-zinc-900 hover:bg-zinc-100">
                        {sidebarAds[1].cta}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Trending Topics */}
              <Card className="border-2 border-foreground/10">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <TrendingUp className="w-5 h-5" />
                    <h3 className="font-bold text-lg">Trending</h3>
                  </div>
                  <div className="space-y-1">
                    {trendingTopics.map((topic, index) => (
                      <a 
                        key={topic}
                        href="#" 
                        className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-muted transition-colors group"
                      >
                        <span className="text-sm font-bold text-muted-foreground w-5">{String(index + 1).padStart(2, '0')}</span>
                        <span className="text-sm font-medium group-hover:text-foreground transition-colors">{topic}</span>
                      </a>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Apps */}
              <Card className="border-2 border-foreground/10">
                <CardContent className="p-6">
                  <h3 className="font-bold text-lg mb-4">Our Apps</h3>
                  <div className="space-y-3">
                    <Link href="/apps" className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted transition-colors group">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center text-white font-bold">
                        FB
                      </div>
                      <div>
                        <p className="font-medium text-sm group-hover:text-foreground">Firebook</p>
                        <p className="text-xs text-muted-foreground">Social that doesn't suck</p>
                      </div>
                    </Link>
                    <Link href="/apps" className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted transition-colors group">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center text-white font-bold">
                        QR
                      </div>
                      <div>
                        <p className="font-medium text-sm group-hover:text-foreground">qrDude</p>
                        <p className="text-xs text-muted-foreground">QR codes, simplified</p>
                      </div>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </aside>
          </div>
        </div>

        {/* Bottom Banner */}
        <div className="border-t border-border bg-muted/30">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Card className="border-2 border-foreground/10 overflow-hidden relative">
              <CardContent className="p-6 sm:p-8">
                <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
                  <div className="flex items-center gap-4">
                    <img 
                      src="/upload/retro-dll-logo.png" 
                      alt="DudeLogicLabs"
                      className="h-16 w-auto hidden sm:block"
                    />
                    <div className="text-center sm:text-left">
                      <p className="text-xs uppercase tracking-wider mb-1 text-muted-foreground">Less Enterprise. More Energy.</p>
                      <h3 className="font-bold text-2xl mb-1">
                        Build Something Cool
                      </h3>
                      <p className="text-muted-foreground">Join a community of curious builders making things that matter.</p>
                    </div>
                  </div>
                  <Button className="bg-foreground text-background hover:bg-foreground/90 shrink-0 text-lg px-8 py-6 gap-2">
                    <Rocket className="w-5 h-5" />
                    Get Started
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-foreground text-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="col-span-2 sm:col-span-1">
              <div className="flex items-center gap-3 mb-4">
                <img 
                  src="/upload/retro-dll-logo.png" 
                  alt="DudeLogicLabs" 
                  className="h-12 w-auto"
                />
                <div>
                  <span className="font-bold text-lg">DudeLogicLabs</span>
                  <p className="text-xs text-background/60">Software for the Seriously Curious</p>
                </div>
              </div>
              <p className="text-sm text-background/70 mb-4">A tiny software studio shipping focused tools, lovable apps, and merch for the seriously curious.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Navigate</h4>
              <ul className="space-y-2">
                <li><Link href="/" className="text-sm text-background/70 hover:text-background transition-colors">Blog</Link></li>
                <li><Link href="/apps" className="text-sm text-background/70 hover:text-background transition-colors">Apps</Link></li>
                <li><a href="#" className="text-sm text-background/70 hover:text-background transition-colors">Shop</a></li>
                <li><a href="#" className="text-sm text-background/70 hover:text-background transition-colors">About</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Apps</h4>
              <ul className="space-y-2">
                <li><Link href="/apps" className="text-sm text-background/70 hover:text-background transition-colors">Firebook</Link></li>
                <li><Link href="/apps" className="text-sm text-background/70 hover:text-background transition-colors">qrDude</Link></li>
                <li><a href="#" className="text-sm text-background/70 hover:text-background transition-colors">More Coming</a></li>
                <li><a href="#" className="text-sm text-background/70 hover:text-background transition-colors">API</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2">
                {['Privacy', 'Terms', 'Cookies', 'Contact'].map((link) => (
                  <li key={link}>
                    <a href="#" className="text-sm text-background/70 hover:text-background transition-colors">{link}</a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <Separator className="my-8 bg-background/20" />
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-background/60">
            <p>&copy; 2025 DudeLogicLabs. The Dude Abides.</p>
            <div className="flex gap-6">
              <a href="#" className="hover:text-background transition-colors">Privacy</a>
              <a href="#" className="hover:text-background transition-colors">Terms</a>
              <a href="#" className="hover:text-background transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

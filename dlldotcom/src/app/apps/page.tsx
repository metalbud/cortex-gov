'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { 
  Search, 
  Menu, 
  X, 
  ArrowUpRight,
  Sparkles,
  QrCode,
  Flame,
  Wrench,
  Clock,
  ExternalLink,
  Check
} from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'

// App data
const apps = [
  {
    id: 'firebook',
    name: 'Firebook',
    tagline: 'Social that doesn\'t suck',
    description: 'A fresh take on social networking. No algorithms, no ads, no drama. Just real connections with people who share your interests.',
    icon: Flame,
    status: 'live',
    color: 'from-orange-500 to-red-500',
    features: ['No algorithmic feed', 'Privacy-first', 'Community driven', 'Cross-platform'],
    url: 'https://firebook.app',
    screenshot: '/upload/dll-graffiti-01.png'
  },
  {
    id: 'qrdude',
    name: 'qrDude',
    tagline: 'QR codes, simplified',
    description: 'The friendliest QR code generator on the web. Create, customize, and download QR codes in seconds. Free forever for basic use.',
    icon: QrCode,
    status: 'live',
    color: 'from-amber-500 to-orange-500',
    features: ['Custom styling', 'Batch generation', 'SVG export', 'API access'],
    url: 'https://qrdude.app',
    screenshot: '/upload/dll-graffiti-02.png'
  },
  {
    id: 'dude-tools',
    name: 'Dude Tools',
    tagline: 'Utilities for curious builders',
    description: 'A growing collection of focused, single-purpose tools. JSON formatters, color pickers, text transformers—built to just work.',
    icon: Wrench,
    status: 'coming-soon',
    color: 'from-slate-500 to-zinc-600',
    features: ['Lightweight', 'No sign-up', 'Open source', 'Keyboard friendly'],
    url: '#',
    screenshot: '/upload/dude.png'
  }
]

const upcomingApps = [
  {
    name: 'Focus Mode',
    description: 'Block distractions, get stuff done',
    icon: '🎯'
  },
  {
    name: 'Paste Bin Pro',
    description: 'Code sharing for the modern era',
    icon: '📋'
  },
  {
    name: 'Color Forge',
    description: 'Palette generation for designers',
    icon: '🎨'
  }
]

export default function AppsPage() {
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
              <Link href="/" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Blog</Link>
              <Link href="/apps" className="text-sm font-medium text-foreground">Apps</Link>
              <Link href="#" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Shop</Link>
              <Link href="#" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">About</Link>
            </nav>

            {/* Search & Actions */}
            <div className="flex items-center gap-3">
              <button className="p-2 rounded-full hover:bg-muted transition-colors">
                <Search className="w-5 h-5 text-muted-foreground" />
              </button>
              <Button className="hidden sm:flex bg-foreground text-background hover:bg-foreground/90 gap-2">
                <Sparkles className="w-4 h-4" />
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
                <Link href="/" className="text-sm font-medium text-muted-foreground py-2">Blog</Link>
                <Link href="/apps" className="text-sm font-medium text-foreground py-2">Apps</Link>
                <Link href="#" className="text-sm font-medium text-muted-foreground py-2">Shop</Link>
                <Link href="#" className="text-sm font-medium text-muted-foreground py-2">About</Link>
                <Button className="mt-2 bg-foreground text-background hover:bg-foreground/90 gap-2">
                  <Sparkles className="w-4 h-4" />
                  Stay Curious
                </Button>
              </nav>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {/* Hero Section */}
        <section className="py-16 sm:py-24">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <Badge variant="outline" className="mb-4 text-sm font-medium">
              Less Enterprise. More Energy.
            </Badge>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
              Apps That Don't Suck
            </h1>
            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Focused tools, lovable apps, and experimental projects for the seriously curious. 
              Built by a tiny studio with big ideas.
            </p>
          </div>
        </section>

        {/* Featured Apps */}
        <section className="pb-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {apps.filter(app => app.status === 'live').map((app) => (
                <Card key={app.id} className="overflow-hidden border-2 border-foreground/10 hover:border-foreground/20 transition-colors group">
                  <div className="relative h-48 overflow-hidden bg-gradient-to-br from-zinc-900 to-slate-900">
                    <img 
                      src={app.screenshot} 
                      alt={app.name}
                      className="w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                    <div className="absolute bottom-4 left-4 right-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${app.color} flex items-center justify-center`}>
                          <app.icon className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-white">{app.name}</h3>
                          <p className="text-sm text-white/70">{app.tagline}</p>
                        </div>
                      </div>
                    </div>
                    <Badge className="absolute top-4 right-4 bg-green-500 text-white border-0">
                      Live
                    </Badge>
                  </div>
                  <CardContent className="p-6">
                    <p className="text-muted-foreground mb-6 leading-relaxed">
                      {app.description}
                    </p>
                    <div className="grid grid-cols-2 gap-3 mb-6">
                      {app.features.map((feature) => (
                        <div key={feature} className="flex items-center gap-2 text-sm">
                          <Check className="w-4 h-4 text-green-500" />
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>
                    <Button className="w-full bg-foreground text-background hover:bg-foreground/90 gap-2" asChild>
                      <a href={app.url} target="_blank" rel="noopener noreferrer">
                        Launch App
                        <ArrowUpRight className="w-4 h-4" />
                      </a>
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Coming Soon */}
        <section className="py-16 bg-muted/30 border-y border-border">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <Badge variant="outline" className="mb-4 text-sm">
                <Clock className="w-3 h-3 mr-1" />
                Coming Soon
              </Badge>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">In the Lab</h2>
              <p className="text-muted-foreground max-w-xl mx-auto">
                These projects are currently brewing. Sign up to get early access when they launch.
              </p>
            </div>

            {/* Coming Soon App */}
            <div className="max-w-2xl mx-auto mb-12">
              {apps.filter(app => app.status === 'coming-soon').map((app) => (
                <Card key={app.id} className="border-2 border-dashed border-foreground/20 overflow-hidden">
                  <div className="relative h-40 overflow-hidden bg-gradient-to-br from-zinc-100 to-slate-100 dark:from-zinc-900 dark:to-slate-900">
                    <img 
                      src={app.screenshot} 
                      alt={app.name}
                      className="w-full h-full object-cover opacity-30"
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${app.color} flex items-center justify-center mx-auto mb-2 opacity-70`}>
                          <app.icon className="w-8 h-8 text-white" />
                        </div>
                        <h3 className="text-xl font-bold">{app.name}</h3>
                        <p className="text-sm text-muted-foreground">{app.tagline}</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="absolute top-4 right-4 bg-background">
                      In Development
                    </Badge>
                  </div>
                  <CardContent className="p-6">
                    <p className="text-muted-foreground mb-4 text-center">
                      {app.description}
                    </p>
                    <div className="grid grid-cols-2 gap-3 mb-6">
                      {app.features.map((feature) => (
                        <div key={feature} className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Check className="w-4 h-4 text-muted-foreground/50" />
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>
                    <div className="flex gap-3">
                      <input 
                        type="email" 
                        placeholder="Get notified at launch"
                        className="flex-1 px-4 py-2 rounded-lg border border-foreground/20 bg-background focus:outline-none focus:border-foreground/40 text-sm"
                      />
                      <Button variant="outline" className="shrink-0">
                        Notify Me
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Upcoming Apps Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl mx-auto">
              {upcomingApps.map((app) => (
                <Card key={app.name} className="border border-dashed border-foreground/20 p-4 hover:border-foreground/40 transition-colors">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{app.icon}</span>
                    <div>
                      <h4 className="font-semibold text-sm">{app.name}</h4>
                      <p className="text-xs text-muted-foreground">{app.description}</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Philosophy Section */}
        <section className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center p-6">
                <div className="w-16 h-16 rounded-2xl bg-foreground/5 flex items-center justify-center mx-auto mb-4">
                  <Wrench className="w-8 h-8" />
                </div>
                <h3 className="font-bold text-lg mb-2">Focused Tools</h3>
                <p className="text-sm text-muted-foreground">
                  Each app does one thing really well. No feature bloat, no confusing menus.
                </p>
              </div>
              <div className="text-center p-6">
                <div className="w-16 h-16 rounded-2xl bg-foreground/5 flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8" />
                </div>
                <h3 className="font-bold text-lg mb-2">Lovable Apps</h3>
                <p className="text-sm text-muted-foreground">
                  Software should spark joy. We craft experiences that feel good to use.
                </p>
              </div>
              <div className="text-center p-6">
                <div className="w-16 h-16 rounded-2xl bg-foreground/5 flex items-center justify-center mx-auto mb-4">
                  <ExternalLink className="w-8 h-8" />
                </div>
                <h3 className="font-bold text-lg mb-2">Open & Honest</h3>
                <p className="text-sm text-muted-foreground">
                  No dark patterns, no hidden agendas. Just straightforward software.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 bg-foreground text-background">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Want to Build Something Cool?</h2>
            <p className="text-background/70 mb-8 max-w-xl mx-auto">
              We're always looking for curious collaborators. Have an idea? Let's talk.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" variant="outline" className="bg-transparent border-background text-background hover:bg-background hover:text-foreground">
                Get in Touch
              </Button>
              <Button size="lg" variant="outline" className="bg-transparent border-background text-background hover:bg-background hover:text-foreground">
                View Open Source
              </Button>
            </div>
          </div>
        </section>
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
                <li><a href="https://firebook.app" className="text-sm text-background/70 hover:text-background transition-colors">Firebook</a></li>
                <li><a href="https://qrdude.app" className="text-sm text-background/70 hover:text-background transition-colors">qrDude</a></li>
                <li><a href="#" className="text-sm text-background/70 hover:text-background transition-colors">Dude Tools</a></li>
                <li><a href="#" className="text-sm text-background/70 hover:text-background transition-colors">API</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-sm text-background/70 hover:text-background transition-colors">Privacy</a></li>
                <li><a href="#" className="text-sm text-background/70 hover:text-background transition-colors">Terms</a></li>
                <li><a href="#" className="text-sm text-background/70 hover:text-background transition-colors">Cookies</a></li>
                <li><a href="#" className="text-sm text-background/70 hover:text-background transition-colors">Contact</a></li>
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

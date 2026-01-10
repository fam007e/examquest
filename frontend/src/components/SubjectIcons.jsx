import React from 'react';
import {
  Atom,
  Binary,
  FlaskConical,
  Dna,
  Languages,
  Globe,
  BarChart3,
  Calculator,
  Compass,
  FileText,
  UserCheck,
  BookOpen,
  Music,
  Palette,
  Scale,
  Microscope,
  Cpu,
  Brain,
  PenTool,
  Landmark
} from 'lucide-react';

export const getSubjectIcon = (name, className = "w-6 h-6") => {
  const n = name.toLowerCase();

  // Sciences
  if (n.includes('physics')) return <Atom className={className} />;
  if (n.includes('chem')) return <FlaskConical className={className} />;
  if (n.includes('biol')) return <Dna className={className} />;
  if (n.includes('science') && !n.includes('computer')) return <Microscope className={className} />;

  // Mathematics
  if (n.includes('math') || n.includes('calculus') || n.includes('further') || n.includes('statistics')) {
    return <Calculator className={className} />;
  }

  // Computing & IT
  if (n.includes('computer') || n.includes('computing') || n.includes('programming')) {
    return <Binary className={className} />;
  }
  if (n.includes('information tech') || n.includes(' it ') || n.includes('ict')) {
    return <Cpu className={className} />;
  }

  // Business & Economics
  if (n.includes('econom')) return <BarChart3 className={className} />;
  if (n.includes('business') || n.includes('commerce')) return <Scale className={className} />;
  if (n.includes('accounting') || n.includes('finance')) return <BarChart3 className={className} />;

  // Humanities
  if (n.includes('history')) return <Landmark className={className} />;
  if (n.includes('geograph')) return <Globe className={className} />;
  if (n.includes('sociology') || n.includes('psychology')) return <Brain className={className} />;
  if (n.includes('law') || n.includes('legal')) return <Scale className={className} />;

  // Languages
  if (n.includes('english') || n.includes('literature')) return <BookOpen className={className} />;
  if (n.includes('french') || n.includes('spanish') || n.includes('german') ||
    n.includes('arabic') || n.includes('chinese') || n.includes('urdu') ||
    n.includes('language')) {
    return <Languages className={className} />;
  }

  // Arts & Creative
  if (n.includes('art') || n.includes('drawing')) return <Palette className={className} />;
  if (n.includes('music')) return <Music className={className} />;
  if (n.includes('design') || n.includes('technology')) return <Compass className={className} />;
  if (n.includes('media')) return <PenTool className={className} />;

  // Religious & Philosophy
  if (n.includes('religious') || n.includes('islamic') || n.includes('divinity')) {
    return <BookOpen className={className} />;
  }

  // Default
  return <FileText className={className} />;
};

// Get color class based on subject category
export const getSubjectColor = (name) => {
  const n = name.toLowerCase();

  if (n.includes('physics') || n.includes('chem') || n.includes('biol') || n.includes('science')) {
    return 'text-accent-cyan';
  }
  if (n.includes('math') || n.includes('calculus') || n.includes('statistics')) {
    return 'text-accent-blue';
  }
  if (n.includes('computer') || n.includes('it') || n.includes('programming')) {
    return 'text-secondary';
  }
  if (n.includes('english') || n.includes('french') || n.includes('language')) {
    return 'text-accent-amber';
  }
  if (n.includes('history') || n.includes('geograph') || n.includes('econom')) {
    return 'text-accent-emerald';
  }
  if (n.includes('art') || n.includes('music') || n.includes('design')) {
    return 'text-accent-rose';
  }

  return 'text-primary';
};

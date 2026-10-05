"use client";
import { Accordion } from "radix-ui";
import { ChevronDown } from "lucide-react";
import type { ReactNode } from "react";
export function SectionAccordion({ items }: { items: { id: string; title: string; content: ReactNode }[] }) {
  return <Accordion.Root type="multiple" defaultValue={items.slice(0, 1).map((item) => item.id)} className="section-accordion">
    {items.map((item, index) => <Accordion.Item className="accordion-item" value={item.id} key={item.id} id={item.id}>
      <Accordion.Header><Accordion.Trigger className="accordion-trigger"><span className="accordion-number">{String(index + 1).padStart(2, "0")}</span><span>{item.title}</span><ChevronDown size={18} className="accordion-chevron"/></Accordion.Trigger></Accordion.Header>
      <Accordion.Content className="accordion-content"><div>{item.content}</div></Accordion.Content>
    </Accordion.Item>)}
  </Accordion.Root>;
}

"use client"

import { motion } from "framer-motion"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

const faqs = [
  {
    question: "How does the natural language input work?",
    answer: "Simply type your reminder in plain English, like 'Call dentist next Tuesday at 10am'. Our AI will automatically parse the date, time, and details to create your reminder.",
  },
  {
    question: "What notification channels are supported?",
    answer: "We support Email, Telegram, WhatsApp, SMS, and push notifications. Premium and Business plans can use all channels simultaneously.",
  },
  {
    question: "Can I collaborate with my team?",
    answer: "Yes! Our Business plan includes full team collaboration features including shared reminders, task assignments, and team dashboards.",
  },
  {
    question: "How does billing work?",
    answer: "We offer monthly billing with no long-term contracts. You can upgrade, downgrade, or cancel at any time. All plans include a 14-day money-back guarantee.",
  },
  {
    question: "Is my data secure?",
    answer: "Absolutely. We use industry-standard encryption, secure data centers, and never share your data with third parties. We're fully GDPR compliant.",
  },
  {
    question: "Can I integrate with other tools?",
    answer: "Premium and Business plans include integrations with Slack, Discord, Google Calendar, Outlook, and more via our API.",
  },
]

export function FAQ() {
  return (
    <section id="faq" className="py-20 md:py-28">
      <div className="container max-w-3xl">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-lg text-muted-foreground">
            Got questions? We've got answers.
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
        >
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, index) => (
              <AccordionItem key={index} value={`item-${index}`}>
                <AccordionTrigger className="text-left">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </motion.div>
      </div>
    </section>
  )
}

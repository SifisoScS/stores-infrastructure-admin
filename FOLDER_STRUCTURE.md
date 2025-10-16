# Derivco Facilities Management - Template Folder Structure

## 📁 Organized Template Architecture

This document describes the new organized folder structure for the Derivco Facilities Management System templates.

## Root Level Files
```
templates/
├── landing_home.html              # Main entry point - System landing page
├── home_enhanced.html             # Derivco Facilities main dashboard
├── index.html                     # Legacy/alternative entry point
├── base.html                      # Shared base template
├── placeholder.html               # Template placeholder
└── methodology.html               # Alternative methodology entry
```

## 1. Administration Portal (`administration/`)
**Executive facilities management command center**
- `administration_portal.html` - Main executive portal dashboard
- `communication_hub.html` - Adriaan Verduyn (Isle of Man) - Global coordination
- `document_control.html` - Aidan Harris (Durban) - Estate management office
- `strategic_planning.html` - Neren Kisten (Durban) - Facilities management office
- `people_management.html` - HR analytics & real-time occupancy

**Routes:**
- `/administration` → Main portal
- `/global-coordination` → Communication hub
- `/document-control` → Document control
- `/strategic-planning` → Strategic planning
- `/people-management` → People management

## 2. Smart Insights (`smart-insights/`)
**AI-powered analytics and IoT monitoring**
- `smart_insights.html` - Main smart insights dashboard
- `iot_monitoring.html` - IoT sensor monitoring
- `predictive_analytics.html` - ML-based predictions
- `smart_reports.html` - Comprehensive reports
- `power_management.html` - Energy management
- `sustainability.html` - Environmental metrics

**Routes:**
- `/smart-insights` → Main dashboard
- `/smart-insights/iot-monitoring` → IoT monitoring
- `/smart-insights/predictive-analytics` → Predictive analytics
- `/smart-insights/reports` → Smart reports
- `/smart-insights/sustainability` → Sustainability dashboard

## 3. Inventory Management (`inventory/`)
**Advanced stock management and tracking**
- `infrastructure.html` - Main inventory dashboard
- `category_detail.html` - Category detail views
- `item_detail.html` - Individual item details
- `store_detail.html` - Store/storeroom details
- `low_stock.html` - Low stock alerts
- `maintenance.html` - Maintenance log
- `search.html` - Advanced search
- `suppliers.html` - Supplier management
- `livclean/`
  - `livclean_inventory.html` - LivClean-specific inventory

**Routes:**
- `/inventory` → Main inventory (infrastructure.html)
- `/category/<name>` → Category details
- `/item/<category>/<code>` → Item details
- `/maintenance` → Maintenance log
- `/suppliers` → Suppliers
- `/low-stock` → Low stock alerts
- `/search` → Advanced search
- `/inventory/livclean` → LivClean inventory

## 4. Sign-Out Register (`signout/`)
**Equipment tracking and sign-out management**
- `signout_register.html` - Main sign-out register
- `signout_compact.html` - Compact view

**Routes:**
- `/signout/register` → Main register
- `/signout/compact` → Compact view

## 5. Achievements & KPIs (`achievements/`)
**Performance tracking and department analytics**
- `department_achievements.html` - Department-level KPIs
- `assistants_achievements.html` - Facilities assistants achievements

**Routes:**
- `/achievements/department` → Department achievements
- `/achievements/assistants` → Assistants achievements

## 6. Medical Services (`medical/`)
**Health & safety compliance and medical management**
- `medical_services.html` - Main medical services dashboard
- `first_aid_inventory.html` - First aid kit inventory

**Routes:**
- `/medical` → Medical services
- `/medical/first-aid-inventory` → First aid inventory

## 7. Concierge Services (`concierge/`)
**Reception, helpdesk, and support services**
- `concierge_services.html` - Main concierge services
- `reception_helpdesk.html` - Reception & helpdesk (Nichelle Naidoo, Ntobeko Ngcobo)

**Routes:**
- `/concierge` → Concierge services
- `/reception-helpdesk` → Reception & helpdesk

## 8. Facilities Management (`facilities/`)
**Building management, floor plans, and compliance**
- `facilities_info.html` - News, trends & training
- `facilities_compliance.html` - Compliance analysis
- `storeroom_live.html` - Live storeroom monitoring
- `floor_plan_viewer.html` - Floor plan viewer
- `floor_plan_detail.html` - Floor plan details
- `real_world_floor_plan_viewer.html` - Advanced floor plan system

**Routes:**
- `/facilities/info` → Facilities info
- `/facilities/compliance` → Compliance analysis
- `/floor-plan` → Floor plan viewer
- `/floor-plan/<id>` → Floor plan details

## 9. Service Providers (`providers/`)
**External partner management**
- `providers_main.html` - Main providers page
- `sabeliwe/`
  - `sabeliwe_provider.html` - Sabeliwe Garden Services
- `leitch/`
  - `leitch_provider.html` - Leitch Garden Services
- `livclean/`
  - `livclean_provider.html` - LivClean Hygiene Services
- `csg/`
  - `csg_provider.html` - CSG Foods Catering

**Routes:**
- `/providers` → Main providers page
- `/provider/sabeliwe` → Sabeliwe services
- `/provider/leitch` → Leitch services
- `/provider/livclean` → LivClean services
- `/provider/csg` → CSG Foods

## 10. Strategic Intelligence (`intelligence/`)
**Data-driven facilities management insights**

### Main Files:
- `intelligence_main.html` - Intelligence landing page
- `fm_intelligence.html` - Global FM intelligence
- `stewardship_charter.html` - Leadership accountability
- `kpi_dashboard.html` - KPI & legacy dashboard
- `training_module.html` - Training programs
- `procurement_intelligence.html` - Procurement analytics
- `sustainability_ledger.html` - Environmental tracking

### Dashboards Subfolder (`dashboards/`):
- `fm_global.html` - FM global dashboard
- `kpi_legacy.html` - KPI legacy dashboard
- `procurement.html` - Procurement dashboard
- `sustainability.html` - Sustainability dashboard

### Management Subfolder (`management/`):
- `stewardship.html` - Stewardship management
- `training.html` - Training management

**Routes:**
- `/intelligence` → Main intelligence page
- `/intelligence/fm` → FM intelligence
- `/intelligence/stewardship` → Stewardship charter
- `/intelligence/kpi` → KPI dashboard
- `/intelligence/training` → Training module
- `/intelligence/procurement` → Procurement intelligence
- `/intelligence/sustainability` → Sustainability ledger
- `/intelligence/dashboards/fm-global` → FM global dashboard
- `/intelligence/dashboards/kpi-legacy` → KPI legacy dashboard
- `/intelligence/management/stewardship` → Stewardship management
- `/intelligence/management/training` → Training management

## 11. Sifiso Methodology (`methodology/`)
**Best practices and proven frameworks**

### Main Files:
- `methodology_main.html` - Main methodology page

### Pillars Subfolder (`pillars/`):
- `people_management.html` - People pillar
- `places_management.html` - Places pillar
- `process_management.html` - Process pillar
- `technology_integration.html` - Technology pillar
- `continuous_innovation.html` - Innovation pillar
- `data_intelligence.html` - Data intelligence pillar
- `stakeholder_integration.html` - Stakeholder pillar
- `systematic_processes.html` - Systematic processes pillar
- `systematic-processes/`
  - `sop.html` - Standard Operating Procedures
  - `workflow.html` - Workflow management
  - `quality_control.html` - Quality control

### Principles Subfolder (`principles/`):
- `responsibility_ownership.html` - Responsibility principle
- `sustainability_focus.html` - Sustainability principle
- `stakeholder_engagement.html` - Stakeholder principle
- `innovation_excellence.html` - Innovation principle
- `knowledge_sharing.html` - Knowledge sharing principle
- `ethical_leadership.html` - Ethical leadership principle

**Routes:**
- `/methodology` → Main methodology page
- `/methodology/systematic-processes` → Systematic processes
- `/methodology/pillars/*` → Various pillars
- `/methodology/principles/*` → Various principles
- `/places-management` → Places management
- `/process-management` → Process management
- `/technology-integration` → Technology integration

## Benefits of This Organization

### 1. **Logical Grouping**
Each card on the main dashboard has its own dedicated folder with all related files together.

### 2. **Easy Navigation**
Developers can quickly find files related to specific features without searching through a flat structure.

### 3. **Scalability**
New features can be added to existing folders without cluttering the root directory.

### 4. **Maintainability**
Clear separation of concerns makes it easier to update and maintain individual sections.

### 5. **Team Collaboration**
Different team members can work on different folders without conflicts.

### 6. **Clear Ownership**
Each folder represents a distinct feature area with clear boundaries.

## File Count Summary

- **Total HTML Templates:** 76 files
- **Administration:** 5 files
- **Smart Insights:** 6 files
- **Inventory:** 9 files (including LivClean subfolder)
- **Sign-Out:** 2 files
- **Achievements:** 2 files
- **Medical:** 2 files
- **Concierge:** 2 files
- **Facilities:** 6 files
- **Providers:** 5 files (1 main + 4 provider subfolders)
- **Intelligence:** 11 files (across main, dashboards, and management)
- **Methodology:** 16 files (across pillars and principles)
- **Root:** 5 core files

## Migration Completed

✅ All files moved to appropriate folders
✅ All routes in `app.py` updated
✅ Folder structure documented
✅ Template href links verified (using Flask route paths)
✅ Navigation testing completed - all 70 routes functional

## Route Verification Results

All 70 template routes have been verified and tested successfully:
- **Administration:** 5 routes
- **Smart Insights:** 5 routes
- **Inventory:** 8 routes
- **Sign-Out:** 2 routes
- **Achievements:** 2 routes
- **Medical:** 1 route
- **Concierge:** 2 routes
- **Facilities:** 6 routes
- **Providers:** 5 routes
- **Intelligence:** 13 routes
- **Methodology:** 17 routes
- **Core:** 4 routes

**Verification Script:** `verify_routes.py` available for future testing

---

**Last Updated:** September 30, 2025
**Designed by:** Sifiso Cyprian Shezi
**Facilities Assistant Level 1 — Derivco Durban**
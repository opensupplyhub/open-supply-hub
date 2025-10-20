import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, FileText, CheckCircle, AlertCircle, Phone, Globe, Building2, Users, MapPin, Eye, EyeOff, Shield, Lock, Info, Clock, HelpCircle, User, Linkedin, Github, Twitter, ArrowLeft, CalendarIcon, Check, ChevronsUpDown, X, Factory, Award, Leaf, Settings, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem } from "@/components/ui/command";
import { Checkbox } from "@/components/ui/checkbox";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { EligibilitySection } from "@/components/EligibilitySection";
import { Stepper } from "@/components/Stepper";
import { PremiumBetaBadge } from "@/components/PremiumBetaBadge";
import { PremiumBetaBanner } from "@/components/PremiumBetaBanner";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

// Multi-select dropdown component
const MultiSelect = ({ 
  options, 
  value, 
  onChange, 
  placeholder = "Select options..." 
}: { 
  options: string[], 
  value: string[], 
  onChange: (values: string[]) => void,
  placeholder?: string
}) => {
  const [open, setOpen] = useState(false);

  const handleSelect = (optionValue: string) => {
    const newValue = value.includes(optionValue) 
      ? value.filter(v => v !== optionValue)
      : [...value, optionValue];
    onChange(newValue);
  };

  const handleRemove = (optionValue: string) => {
    onChange(value.filter(v => v !== optionValue));
  };

  return (
    <div className="space-y-2">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between"
          >
            {value.length > 0 ? `${value.length} selected` : placeholder}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-full p-0" align="start">
          <Command>
            <CommandInput placeholder="Search options..." />
            <CommandEmpty>No options found.</CommandEmpty>
            <CommandGroup className="max-h-64 overflow-auto">
              {options.map((option) => (
                <CommandItem
                  key={option}
                  value={option}
                  onSelect={() => handleSelect(option)}
                >
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      checked={value.includes(option)}
                      onChange={() => handleSelect(option)}
                    />
                    <span>{option}</span>
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          </Command>
        </PopoverContent>
      </Popover>
      
      {value.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {value.map((item) => (
            <Badge 
              key={item} 
              variant="secondary" 
              className="text-xs px-2 py-1"
            >
              {item}
              <Button
                variant="ghost"
                size="sm"
                className="ml-1 h-auto p-0 text-muted-foreground hover:text-foreground"
                onClick={() => handleRemove(item)}
              >
                <X className="h-3 w-3" />
              </Button>
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
};

const ClaimsForm = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const userRole = location.state?.userRole || "";
  const isNonManager = userRole === "employee_no_authority";
  
  const [activeTab, setActiveTab] = useState("eligibility");
  const [completedSections, setCompletedSections] = useState<string[]>([]);
  const [isContactSameAsClaimant, setIsContactSameAsClaimant] = useState(true);
  const [verificationMethod, setVerificationMethod] = useState("");
  const [companyAddressVerification, setCompanyAddressVerification] = useState("");
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [businessValidationErrors, setBusinessValidationErrors] = useState<string[]>([]);
  
  // Eligibility state
  const [ownerManagerDecision, setOwnerManagerDecision] = useState("");
  const [businessAccountDecision, setBusinessAccountDecision] = useState("");
  const [brandSelection, setBrandSelection] = useState("");
  const [otherBrandText, setOtherBrandText] = useState("");
  const [formData, setFormData] = useState({
    // Claimant fields (person filling form)
    claimantName: "",
    claimantTitle: "",
    claimantEmail: "",
    websiteProof: "",
    namePublic: false,
    titlePublic: false,
    // Supervisor fields (for non-managers)
    supervisorName: "",
    supervisorTitle: "",
    supervisorEmail: "",
    supervisorPhone: "",
    // Production location contact fields (if different from claimant)
    contactName: "",
    contactEmail: "",
    contactNamePublic: "false",
    contactEmailPublic: "false",
    // Business fields  
    businessWebsite: "",
    linkedinProfile: "",
    parentCompanyName: "",
    officeName: "",
    officeAddress: "",
    officeCountry: "",
    officePhone: "",
    // Production location fields
    facilityName: "ABC Manufacturing Ltd.",
    sector: [],
    facilityPhone: "",
    address: "123 Industrial Park Road, Manufacturing District, State 12345, Country",
    facilityWebsite: "",
    localLanguageName: "",
    numberOfWorkers: "",
    femaleWorkers: "",
    minimumOrderQuantity: "",
    averageLeadTime: "",
    facilityTypes: [],
    productTypes: "",
    openingDate: null as Date | null,
    closingDate: null as Date | null,
    throughput: "",
    energyConsumption: {
      coal: { selected: false, value: "" },
      naturalGas: { selected: false, value: "" },
      diesel: { selected: false, value: "" },
      kerosene: { selected: false, value: "" },
      biomass: { selected: false, value: "" },
      charcoal: { selected: false, value: "" },
      animalWaste: { selected: false, value: "" },
      electricity: { selected: false, value: "" },
      other: { selected: false, value: "" }
    },
    affiliations: [],
    certifications: [],
    description: ""
  });
  const [publicVisibilityEnabled, setPublicVisibilityEnabled] = useState(false);

  const markSectionComplete = (section: string) => {
    if (!completedSections.includes(section)) {
      setCompletedSections([...completedSections, section]);
    }
  };

  const updateFormData = (field: string, value: string | Date | null | any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const SECTOR_OPTIONS = [
    "Accommodation", "Aerospace", "Agriculture", "Air Transportation", "Allied Products", "Animal Production", "Apparel", "Apparel Accessories", "Appliances", "Aquaculture", "Archives", "Arts", "Arts & Entertainment", "Automotive", "Automotive Parts", "Banking", "Beauty Products", "Beverages", "Biotechnology", "Books", "Building Construction", "Building Materials", "Chemicals", "Civics", "Civil Engineering Construction", "Coal", "Commodities", "Components", "Computers", "Computing Infrastructure", "Construction", "Consumer Electronics", "Consumer Products", "Crop Production", "Durable Goods", "Educational Services", "Electrical Devices", "Electricity", "Electronic Product Manufacturing", "Electronics", "Energy", "Energy Production & Utilities", "Entertainment", "Equipment", "Farming", "Finance", "Financial Services", "Fishing", "Food", "Food & Beverage", "Food Industry", "Food Manufacturing", "Footwear", "Forestry", "Furniture", "Garden Tools", "Gas", "General Merchandise", "Ground Passenger Transportation", "Hard Goods", "Health", "Healthcare", "Hobby", "Home", "Home Accessories", "Home Furnishings", "Hospitals", "Home Textiles", "Hunting", "Information", "International Affairs", "Jewelry", "Leather", "Logging", "Machinery Manufacturing", "Maintenance", "Manufacturing", "Maritime Transportation", "Material Production", "Medical Equipment & Services", "Merchant Wholesalers", "Metal Manufacturing", "Mining", "Multi-Category", "Musical Instruments", "Nondurable Goods", "Nursing", "Oil & Gas", "Packaging", "Paper Products", "Parts Dealers", "Personal Care Products", "Pets", "Pharmaceuticals", "Pipeline Transportation", "Plastics", "Printing", "Professional Services", "Quarrying", "Rail Transportation", "Recreation", "Recycling", "Renewable Energy", "Renting", "Repair", "Research", "Rubber Products", "Solar Energy", "Specialty Trade Contractors", "Sports Equipment", "Sporting Goods", "Storage", "Supplies Dealers", "Technical and Scientific Activities", "Technical Services", "Technology", "Telecommunications", "Textiles", "Tobacco Products", "Toys", "Transportation Equipment", "Trucking", "Utilities", "Waste Management", "Water Utilities", "Warehousing", "Wholesale Trade", "Wood Products"
  ];

  const PROCESSING_TYPE_OPTIONS = [
    "Biological Recycling", "Boiling", "Breeding", "Chemical Recycling", "Chemical Synthesis", "Collecting", "Concentrating", "Disassembly", "Down Processing", "Dry Spinning", "Extrusion", "Ginning", "Hatchery", "Mechanical Recycling", "Melt Spinning", "Preparation", "Preparatory", "Processing Site", "Pulp making", "Raw Material Processing or Production", "Retting", "Scouring", "Shredding", "Slaughterhouse", "Slaughtering", "Sorting", "Spinning", "Standardization/ Chemical finishing", "Synthetic Leather Production", "Tannery", "Tanning", "Textile Recycling", "Top making", "Twisting/Texturizing Facility", "Wet Spinning", "Yarn spinning", "Blending", "Bonding", "Buffing", "Components", "Doubling", "Embellishment", "Embossing", "Embroidery", "Fabric Mill", "Flat Knit", "Fusing", "Garment Accessories Manufacturing", "Knitting", "Circular Knitting", "Lace Knitting", "Knitting Seamless", "Knitting V Bed", "Knitting Warp", "Laminating", "Material Creation", "Material Production", "Mill", "Non woven manufacturing", "Non-woven Processing", "Painting", "Pressing", "Pelletizing", "Spraying", "Straight bar knitting", "Textile or Material Production", "Textile Mill", "Weaving", "Welding", "Batch Dyeing", "Coating", "Continuous dyeing", "Direct Digital Ink Printing", "Dyeing", "Fabric All Over Print", "Fabric Chemical Finishing", "Finishing", "Fiber Dye", "Flat Screen Printing", "Garment Dyeing", "Garment Place Print", "Garment Wash", "Garment Finishing", "Hand Dye", "Laundering", "Laundry", "Pre-treatment", "Printing", "Printing, Product Dyeing and Laundering", "Product Dyeing", "Rotary Printing", "Screen Printing", "Spray Dye", "Sublimation", "Textile Dyeing", "Textile Printing", "Textile Chemical Finishing", "Textile Mechanical Finishing", "Tye Dye", "Washing", "Wet Processing", "Wet roller printing", "Yarn Dyeing", "Assembly", "Cutting", "Cut & Sew", "Embellishment", "Embroidery", "Final Product Assembly", "Finished Goods", "Ironing", "Knitwear Assembly", "Knit Composite", "Linking", "Manufacturing", "Making up", "Marker Making", "Molding", "Packaging", "Pattern Grading", "Pleating", "Pressing", "Product Finishing", "Ready Made Garment", "Sample Making", "Seam taping", "Sewing", "Steaming", "Stitching", "Tailoring", "Headquarters", "No processing", "Office", "Office / HQ", "Sourcing Agent", "Trading", "Packing", "Warehousing / Distribution", "Recruitment Agency"
  ];

  const AFFILIATIONS_OPTIONS = [
    "Better Mills Program",
    "Canopy",
    "Sustainable Apparel Coalition",
    "Fashion Revolution",
    "Ellen MacArthur Foundation",
    "Textile Exchange",
    "Fair Labor Association",
    "Better Cotton Initiative",
    "Global Organic Textile Standard (GOTS)",
    "Cradle to Cradle Certified",
    "Bluesign",
    "OEKO-TEX"
  ];

  const CERTIFICATIONS_OPTIONS = [
    "BCI (Better Cotton Initiative)",
    "B Corp",
    "ISO 9001",
    "ISO 14001", 
    "OEKO-TEX Standard 100",
    "GOTS (Global Organic Textile Standard)",
    "Cradle to Cradle Certified",
    "Bluesign",
    "WRAP (Worldwide Responsible Accredited Production)",
    "SA8000",
    "BSCI (Business Social Compliance Initiative)",
    "Fairtrade",
    "Organic Content Standard (OCS)",
    "Recycled Claim Standard (RCS)",
    "Global Recycled Standard (GRS)"
  ];

  const updateEnergyConsumption = (source: string, field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      energyConsumption: {
        ...prev.energyConsumption,
        [source]: {
          ...prev.energyConsumption[source],
          [field]: value
        }
      }
    }));
  };

  const togglePublicVisibility = () => {
    setPublicVisibilityEnabled(prev => !prev);
  };

  const isContactValid = () => {
    const baseValidation = formData.claimantName && formData.claimantTitle && formData.claimantEmail && verificationMethod;
    
    if (isNonManager) {
      return baseValidation && formData.supervisorName && formData.supervisorTitle && 
             formData.supervisorEmail && formData.supervisorPhone;
    }
    
    return baseValidation;
  };

  const validateContactFields = () => {
    const errors: string[] = [];
    if (!formData.claimantName) errors.push("claimantName");
    if (!formData.claimantTitle) errors.push("claimantTitle");
    if (!verificationMethod) errors.push("verificationMethod");
    
    if (isNonManager) {
      if (!formData.supervisorName) errors.push("supervisorName");
      if (!formData.supervisorTitle) errors.push("supervisorTitle");
      if (!formData.supervisorEmail) errors.push("supervisorEmail");
      if (!formData.supervisorPhone) errors.push("supervisorPhone");
    }
    
    setValidationErrors(errors);
    return errors.length === 0;
  };

  const validateBusinessFields = () => {
    const errors: string[] = [];
    if (!companyAddressVerification) errors.push("companyAddressVerification");
    
    // Check if URL is required and filled
    if ((companyAddressVerification === "business-website" ||
         companyAddressVerification === "company-website-address" || 
         companyAddressVerification === "linkedin-address") && 
        !formData.businessWebsite) {
      errors.push("verificationUrl");
    }
    
    setBusinessValidationErrors(errors);
    return errors.length === 0;
  };

  const isBusinessValid = () => {
    if (!companyAddressVerification) return false;
    
    // If URL-based verification, check if URL is provided
    if (companyAddressVerification === "business-website" ||
        companyAddressVerification === "company-website-address" || 
        companyAddressVerification === "linkedin-address") {
      return formData.businessWebsite !== "";
    }
    
    return true;
  };

  const isEligibilityValid = () => {
    return ["owner", "manager", "parent_company", "employee_no_authority"].includes(businessAccountDecision);
  };

  const progress = (completedSections.length / 4) * 100;

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-white">
        {/* Header */}
        <header className="border-b border-gray-200 bg-white">
          <div className="container mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
                <div className="grid grid-cols-2 gap-0.5">
                  <div className="w-1.5 h-1.5 bg-white rounded-sm"></div>
                  <div className="w-1.5 h-1.5 bg-white rounded-sm"></div>
                  <div className="w-1.5 h-1.5 bg-white rounded-sm"></div>
                  <div className="w-1.5 h-1.5 bg-white rounded-sm"></div>
                </div>
              </div>
              <span className="font-bold text-lg text-black">OPEN SUPPLY HUB</span>
            </div>
            
            <nav className="hidden md:flex items-center space-x-6">
              <Button variant="ghost" className="text-black hover:text-black">Explore</Button>
              <Button variant="ghost" className="text-black hover:text-black">How It Works</Button>
              <Button variant="ghost" className="text-black hover:text-black">About Us</Button>
              <Button variant="ghost" className="text-black hover:text-black">Pricing</Button>
              <Globe className="w-5 h-5 text-black" />
              <User className="w-5 h-5 text-black" />
              <span className="text-sm text-black">My Account</span>
              <Button className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold">Add Data</Button>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="py-4 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="mb-4 text-center">
            <h1 className="text-2xl font-bold mb-1">Production Location Claims Process</h1>
            <p className="text-muted-foreground mb-3 text-sm">
              Complete all sections to submit your production location claim
            </p>
            <div className="max-w-md mx-auto">
              <Progress value={progress} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">
                {completedSections.length} of 4 sections completed
              </p>
            </div>
          </div>

          <Stepper
            steps={[
              {
                id: "eligibility",
                title: "Eligibility Check",
                icon: <Shield className="h-5 w-5" />,
                timeEstimate: "1 min"
              },
              {
                id: "contact",
                title: "Contact",
                icon: <Users className="h-5 w-5" />,
                subtitle: "Step 1",
                timeEstimate: "5 mins"
              },
              {
                id: "business",
                title: "Business",
                icon: <Globe className="h-5 w-5" />,
                subtitle: "Step 2",
                timeEstimate: "3 mins"
              },
              {
                id: "facility",
                title: "Open Supply Hub Profile",
                icon: <Building2 className="h-5 w-5" />,
                subtitle: "Step 3",
                timeEstimate: "10 mins"
              }
            ]}
            currentStep={activeTab}
            completedSteps={completedSections}
            onStepClick={setActiveTab}
          />

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">

          {/* Eligibility Tab */}
          <TabsContent value="eligibility">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Eligibility Check
                </CardTitle>
                <CardDescription>
                  Please verify that this account is eligible to claim this production location
                </CardDescription>
              </CardHeader>
              <CardContent>
                <EligibilitySection
                  ownerManagerDecision={ownerManagerDecision}
                  setOwnerManagerDecision={setOwnerManagerDecision}
                  businessAccountDecision={businessAccountDecision}
                  setBusinessAccountDecision={setBusinessAccountDecision}
                  brandSelection={brandSelection}
                  setBrandSelection={setBrandSelection}
                  otherBrandText={otherBrandText}
                  setOtherBrandText={setOtherBrandText}
                />
                
                <div className="flex justify-between mt-6">
                  <Button 
                    variant="outline"
                    onClick={() => navigate("/")}
                    className="px-6 py-2 text-sm font-semibold"
                  >
                    GO BACK
                  </Button>
                  <Button 
                    onClick={() => {
                      if (isEligibilityValid()) {
                        markSectionComplete("eligibility");
                        setActiveTab("contact");
                      }
                    }}
                    disabled={!isEligibilityValid()}
                    className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold"
                  >
                    Continue to Contact Information →
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="contact">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Contact Information
                </CardTitle>
                <CardDescription>
                  Provide your information and production location contact details
                </CardDescription>
              </CardHeader>
               <CardContent className="space-y-3">
                 {/* Claimant Information */}
                  <div className="space-y-2">
                  <h4 className="font-medium">Your Information (Claimant)</h4>
                  
                  <div className="space-y-2">
                     <div className="flex items-center justify-between">
                       <Label htmlFor="claimant-email" className="flex items-center gap-1">
                         Your Email
                         <span className="text-red-500">*</span>
                       </Label>
                     </div>
                    <Input 
                      id="claimant-email" 
                      type="email"
                      value={formData.claimantEmail || "opensupplyhubuser@company.com"}
                      onChange={(e) => updateFormData("claimantEmail", e.target.value)}
                      placeholder="opensupplyhubuser@company.com"
                      className="text-foreground bg-muted"
                      required
                      readOnly
                    />
                  </div>

                   <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                     <div className="space-y-2">
                         <div className="flex items-center justify-between">
                           <Label htmlFor="claimant-name" className="flex items-center gap-1">
                              Your Name
                              <span className="text-red-500">*</span>
                            </Label>
                            <div
                              className="flex items-center gap-2 text-xs invisible pointer-events-none"
                              aria-hidden="true"
                            >
                              <Switch defaultChecked={false} />
                              <span className="text-muted-foreground">Private</span>
                              <EyeOff className="h-3 w-3 text-muted-foreground" />
                            </div>
                        </div>
                      <Input 
                        id="claimant-name" 
                        value={formData.claimantName}
                        onChange={(e) => {
                          updateFormData("claimantName", e.target.value);
                          if (validationErrors.includes("claimantName")) {
                            setValidationErrors(validationErrors.filter(e => e !== "claimantName"));
                          }
                        }}
                        placeholder="Enter your full name" 
                        required
                        className={validationErrors.includes("claimantName") ? "bg-[hsl(var(--error-light))]" : ""}
                      />
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label htmlFor="claimant-title" className="flex items-center gap-1">
                          Your Job Title
                          <span className="text-red-500">*</span>
                        </Label>
                        <div
                          className="flex items-center gap-2 text-xs invisible pointer-events-none"
                          aria-hidden="true"
                        >
                          <Switch defaultChecked={false} />
                          <span className="text-muted-foreground">Private</span>
                          <EyeOff className="h-3 w-3 text-muted-foreground" />
                        </div>
                      </div>
                      <Input 
                        id="claimant-title" 
                        value={formData.claimantTitle}
                        onChange={(e) => {
                          updateFormData("claimantTitle", e.target.value);
                          if (validationErrors.includes("claimantTitle")) {
                            setValidationErrors(validationErrors.filter(e => e !== "claimantTitle"));
                          }
                        }}
                        placeholder="e.g., Plant Manager, Safety Director" 
                        required
                        className={validationErrors.includes("claimantTitle") ? "bg-[hsl(var(--error-light))]" : ""}
                      />
                    </div>
                  </div>

                  {/* Disclaimer */}
                  <div className="bg-muted/50 rounded-lg p-2.5 mt-3">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="h-3 w-3 text-destructive mt-0.5" />
                      <div className="text-xs">
                        <span className="font-medium text-destructive">IMPORTANT!</span> Your name and job title must match the person associated with the email address provided above.
                      </div>
                    </div>
                  </div>

                  {/* Employment Verification Section */}
                  <div className="space-y-2 mt-3">
                    <div className="space-y-1">
                      <h4 className="font-medium flex items-center gap-1">
                        Employment Verification
                        <span className="text-red-500">*</span>
                      </h4>
                      <p className="text-xs text-muted-foreground">
                        You need to select and provide one of the below items for employment verification.
                      </p>
                    </div>

                    <div className="space-y-2">
                      <Select value={verificationMethod} onValueChange={(value) => {
                        setVerificationMethod(value);
                        if (validationErrors.includes("verificationMethod")) {
                          setValidationErrors(validationErrors.filter(e => e !== "verificationMethod"));
                        }
                      }}>
                        <SelectTrigger className={cn("w-full bg-white border-gray-300", validationErrors.includes("verificationMethod") && "bg-[hsl(var(--error-light))]")}>
                          <SelectValue placeholder="Choose ONE" />
                        </SelectTrigger>
                         <SelectContent className="bg-white border border-gray-300 shadow-lg z-50">
                          <SelectItem value="employment-letter">
                            Employment letter or contract showing your name, title, and company
                          </SelectItem>
                          <SelectItem value="signed-stamped-letter">
                            Signed and/or stamped letter on company letterhead that confirms your name, your title with the company, and your email address
                          </SelectItem>
                          <SelectItem value="company-id">
                            Company ID badge or access card (photo showing name and title)
                          </SelectItem>
                          <SelectItem value="org-chart">
                            Official organizational chart showing your position
                          </SelectItem>
                          <SelectItem value="business-card">
                            Business card showing your name, title and company
                          </SelectItem>
                          <SelectItem value="company-website">
                            Company website showing your name and title (e.g., About Us, Team page)
                          </SelectItem>
                          <SelectItem value="official-document">
                            An official company document showing your name and title
                          </SelectItem>
                          <SelectItem value="audit-reports">
                            Audit reports showing your name and role at the facility
                          </SelectItem>
                          <SelectItem value="linkedin">
                            Your LinkedIn page showing your name, title and company
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Conditional sections based on verification method */}
                    {verificationMethod && (
                      <div className="mt-3 space-y-3">
                        {(verificationMethod === "employment-letter" || 
                          verificationMethod === "signed-stamped-letter" ||
                          verificationMethod === "company-id" || 
                          verificationMethod === "org-chart" || 
                          verificationMethod === "business-card" || 
                          verificationMethod === "official-document") && (
                          <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors cursor-pointer">
                            <Upload className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
                            <p className="text-sm font-medium mb-2">Upload your documents/photos</p>
                            <p className="text-xs text-muted-foreground mb-4">
                              Please upload one or more clear photos or scans of your selected verification method. You can upload multiple files.
                            </p>
                            <Button variant="outline" size="sm">
                              Choose Files
                            </Button>
                          </div>
                        )}
                        
                        {verificationMethod === "audit-reports" && (
                          <div className="space-y-3">
                            <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors cursor-pointer">
                              <Upload className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
                              <p className="text-sm font-medium mb-2">Upload audit documents</p>
                              <p className="text-xs text-muted-foreground mb-4">
                                Upload one or more PDF, DOC, DOCX, or image files (max 10MB each)
                              </p>
                              <Button type="button" variant="outline" size="sm">
                                Choose Files
                              </Button>
                            </div>
                            
                            <div className="flex items-center justify-center space-x-4">
                              <div className="h-px bg-border flex-1"></div>
                              <span className="text-xs text-muted-foreground">OR</span>
                              <div className="h-px bg-border flex-1"></div>
                            </div>
                            
                            <div className="space-y-2">
                              <Label htmlFor="audit-url" className="flex items-center gap-1">
                                Link to One Audit Report
                                <span className="text-red-500">*</span>
                              </Label>
                              <Input 
                                id="audit-url" 
                                type="url"
                                placeholder="https://example.com/audit-report.pdf"
                                className="text-foreground"
                              />
                            </div>
                          </div>
                        )}
                        
                        {(verificationMethod === "company-website" || verificationMethod === "linkedin") && (
                          <div className="space-y-2">
                            <Label htmlFor="verification-url" className="flex items-center gap-1">
                              {verificationMethod === "linkedin" ? "LinkedIn Profile URL" : "Website URL"}
                              <span className="text-red-500">*</span>
                            </Label>
                            <Input 
                              id="verification-url" 
                              type="url"
                              placeholder={verificationMethod === "linkedin" ? "https://linkedin.com/in/yourprofile" : "https://company.com/about-us"}
                              className="text-foreground"
                              required
                            />
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Supervisor Verification (for non-managers) */}
                {isNonManager && (
                  <div className="space-y-3 mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="space-y-1.5">
                      <h4 className="font-medium text-lg text-blue-900 flex items-center gap-1">
                        Supervisor/Manager Verification Required
                        <Badge className="bg-blue-600 hover:bg-blue-600 text-white text-xs px-1.5 py-0 h-4">*</Badge>
                      </h4>
                      <p className="text-sm text-blue-800">
                        Since you indicated that you don't have management authority, please provide your supervisor or manager's contact information. We will reach out to them to verify your employment and authority to submit this claim. Additional documentation may be requested during the verification process.
                      </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="supervisor-name" className="flex items-center gap-1">
                          Supervisor/Manager Name
                          <span className="text-red-500">*</span>
                        </Label>
                        <Input 
                          id="supervisor-name" 
                          value={formData.supervisorName}
                          onChange={(e) => {
                            updateFormData("supervisorName", e.target.value);
                            if (validationErrors.includes("supervisorName")) {
                              setValidationErrors(validationErrors.filter(e => e !== "supervisorName"));
                            }
                          }}
                          placeholder="Enter supervisor's full name" 
                          required
                          className={validationErrors.includes("supervisorName") ? "bg-[hsl(var(--error-light))]" : ""}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="supervisor-title" className="flex items-center gap-1">
                          Supervisor/Manager Title
                          <span className="text-red-500">*</span>
                        </Label>
                        <Input 
                          id="supervisor-title" 
                          value={formData.supervisorTitle}
                          onChange={(e) => {
                            updateFormData("supervisorTitle", e.target.value);
                            if (validationErrors.includes("supervisorTitle")) {
                              setValidationErrors(validationErrors.filter(e => e !== "supervisorTitle"));
                            }
                          }}
                          placeholder="e.g., Plant Manager, Director" 
                          required
                          className={validationErrors.includes("supervisorTitle") ? "bg-[hsl(var(--error-light))]" : ""}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="supervisor-email" className="flex items-center gap-1">
                          Supervisor/Manager Email
                          <span className="text-red-500">*</span>
                        </Label>
                        <Input 
                          id="supervisor-email" 
                          type="email"
                          value={formData.supervisorEmail}
                          onChange={(e) => {
                            updateFormData("supervisorEmail", e.target.value);
                            if (validationErrors.includes("supervisorEmail")) {
                              setValidationErrors(validationErrors.filter(e => e !== "supervisorEmail"));
                            }
                          }}
                          placeholder="supervisor@company.com" 
                          required
                          className={validationErrors.includes("supervisorEmail") ? "bg-[hsl(var(--error-light))]" : ""}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="supervisor-phone" className="flex items-center gap-1">
                          Supervisor/Manager Phone
                          <span className="text-red-500">*</span>
                        </Label>
                        <Input 
                          id="supervisor-phone" 
                          type="tel"
                          value={formData.supervisorPhone}
                          onChange={(e) => {
                            updateFormData("supervisorPhone", e.target.value);
                            if (validationErrors.includes("supervisorPhone")) {
                              setValidationErrors(validationErrors.filter(e => e !== "supervisorPhone"));
                            }
                          }}
                          placeholder="+1 (555) 123-4567" 
                          required
                          className={validationErrors.includes("supervisorPhone") ? "bg-[hsl(var(--error-light))]" : ""}
                        />
                      </div>
                    </div>

                    <div className="bg-blue-100 border border-blue-300 rounded p-3">
                      <p className="text-xs text-blue-800">
                        <strong>Note:</strong> Your claim will be placed in a pending status until we receive verification from your supervisor/manager. The verification process typically takes 3-5 business days.
                      </p>
                    </div>
                  </div>
                )}

                {/* Premium Beta Banner */}
                <PremiumBetaBanner />

                {/* Facility Contact Information */}
                <div className="space-y-3">
                  <h4 className="font-medium text-lg">Production Location Contact Person</h4>
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <h5 className="font-medium text-amber-800 mb-0.5">Are you the primary contact for this production location?</h5>
                        <p className="text-sm text-amber-700">Toggle if you are the main contact person for production location inquiries</p>
                      </div>
                       <div className="flex flex-col gap-1 items-center">
                         <Switch 
                           checked={isContactSameAsClaimant}
                           onCheckedChange={setIsContactSameAsClaimant}
                         />
                         <span className="text-sm text-amber-700">{isContactSameAsClaimant ? "Yes" : "No"}</span>
                       </div>
                    </div>
                  </div>
                  
                  {!isContactSameAsClaimant && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4">
                        <div className="space-y-2">
                           <Label htmlFor="contact-name" className="inline-flex items-center">
                             Contact Name
                             <PremiumBetaBadge />
                           </Label>
                        <Input 
                          id="contact-name" 
                          value={formData.contactName}
                          onChange={(e) => updateFormData("contactName", e.target.value)}
                          placeholder="Contact person's name" 
                        />
                      </div>
                        <div className="space-y-2">
                           <Label htmlFor="contact-email" className="inline-flex items-center">
                             Contact Email
                             <PremiumBetaBadge />
                           </Label>
                        <Input 
                          id="contact-email" 
                          type="email"
                          value={formData.contactEmail}
                          onChange={(e) => updateFormData("contactEmail", e.target.value)}
                          placeholder="contact@company.com" 
                        />
                      </div>
                     </div>
                   )}
                 </div>

                 {/* Master Public Visibility Toggle */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 space-y-2 relative">
                    <X className="absolute inset-0 w-full h-full text-red-600 opacity-30 p-4" strokeWidth={3} />
                    <span className="absolute top-3 right-3 text-red-600 text-3xl font-bold z-10">?</span>
                   <div className="flex items-center justify-between gap-3">
                     <div>
                         <h4 className="font-medium text-blue-900">
                           Public Visibility Settings
                         </h4>
                        <p className="text-sm text-blue-800 mt-0.5">
                          Do you want this contact information to be publicly displayed on the production location profile?
                        </p>
                     </div>
                      <div className="flex flex-col gap-1 items-center">
                        <Switch 
                          checked={publicVisibilityEnabled}
                          onCheckedChange={togglePublicVisibility}
                        />
                        <div className="flex items-center gap-1">
                          <span className="text-sm font-medium text-blue-900">
                            {publicVisibilityEnabled ? "Public" : "Private"}
                          </span>
                          {publicVisibilityEnabled ? (
                            <Eye className="h-4 w-4 text-blue-600" />
                          ) : (
                            <EyeOff className="h-4 w-4 text-blue-600" />
                          )}
                        </div>
                      </div>
                   </div>
                 </div>

                 <div className="flex justify-between items-center pt-3">
                  <Button
                    variant="outline"
                    onClick={() => navigate("/")}
                    className="bg-pink hover:bg-pink/90 text-pink-foreground border-pink"
                  >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Go Back
                  </Button>
                  
                  <Button 
                    onClick={() => {
                      if (validateContactFields()) {
                        markSectionComplete("contact");
                        setActiveTab("business");
                      }
                    }}
                    className={isContactValid() ? "bg-green-600 hover:bg-green-700" : ""}
                  >
                    Continue to Business Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="business">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="h-5 w-5" />
                  Business Information
                </CardTitle>
                <CardDescription>
                  Verify the company address for this production location
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {/* Production Location Name and Address */}
                <div className="space-y-1.5">
                  <h4 className="font-medium text-base">Production Location Details</h4>
                  <div className="space-y-2 pl-3">
                    <div className="space-y-1.5">
                      <Label htmlFor="os-id">OS ID</Label>
                      <a 
                        href="https://opensupplyhub.org/facilities/CN2021250D1DTN7"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block w-full px-3 py-2 bg-muted rounded-md border border-input text-blue-600 hover:text-blue-800 underline"
                      >
                        CN2021250D1DTN7
                      </a>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="space-y-1.5">
                        <Label htmlFor="facility-name">Company Name</Label>
                        <Input 
                          id="facility-name" 
                          value={formData.facilityName}
                          disabled
                          className="bg-muted cursor-not-allowed"
                          placeholder="Textile Manufacturing Plant - Sample Location" 
                        />
                      </div>
                      <div className="space-y-1.5">
                        <Label htmlFor="address">Company Address</Label>
                        <Textarea 
                          id="address" 
                          value={formData.address}
                          disabled
                          placeholder="Street address, city, state/province, postal code, country"
                          className="min-h-[80px] bg-muted cursor-not-allowed"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Company Address Verification Section */}
                <div className="space-y-1.5 mt-2">
                  <div className="space-y-1">
                    <h4 className="font-medium text-base flex items-center gap-1">
                      Company Address Verification
                      <span className="text-red-500">*</span>
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      You need to select and provide one of the below items for company address verification.
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <Select value={companyAddressVerification} onValueChange={setCompanyAddressVerification}>
                      <SelectTrigger className={cn(
                        "w-full bg-white border-gray-300",
                        businessValidationErrors.includes("companyAddressVerification") && "bg-red-50 border-red-300"
                      )}>
                        <SelectValue placeholder="Choose ONE" />
                      </SelectTrigger>
                      <SelectContent className="bg-white border border-gray-300 shadow-lg z-50">
                        {/* Business Website Options */}
                        <SelectItem value="company-website-address">
                          Company website showing the production location address (e.g., Contact Us, Locations page)
                        </SelectItem>
                        <SelectItem value="linkedin-address">
                          Company LinkedIn page showing the production location address
                        </SelectItem>
                        
                        {/* Document Upload Options */}
                        <SelectItem value="utility-bill">
                          Utility bill showing company name and address
                        </SelectItem>
                        <SelectItem value="business-registration">
                          Business registration document
                        </SelectItem>
                        <SelectItem value="tax-license">
                          Tax document or business license
                        </SelectItem>
                        <SelectItem value="property-lease">
                          Property lease or ownership document
                        </SelectItem>
                        <SelectItem value="official-documents">
                          Upload other official documents (business registration, utility bills, etc.)
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Conditional sections based on verification method */}
                  {companyAddressVerification && (
                    <div className="mt-2 space-y-2">
                      {/* Document Upload Cases */}
                      {(companyAddressVerification === "utility-bill" || 
                        companyAddressVerification === "business-registration" || 
                        companyAddressVerification === "tax-license" || 
                        companyAddressVerification === "property-lease" ||
                        companyAddressVerification === "official-documents") && (
                        <div className={cn(
                          "border-2 border-dashed border-border rounded-lg p-3 text-center hover:border-primary/50 transition-colors cursor-pointer",
                          businessValidationErrors.includes("documentUpload") && "bg-red-50 border-red-300"
                        )}>
                          <Upload className="h-7 w-7 mx-auto mb-2 text-muted-foreground" />
                          <p className="text-sm font-medium mb-1">Upload your documents</p>
                          <p className="text-xs text-muted-foreground mb-2">
                            Please upload one or more clear photos or scans of your selected verification documents
                          </p>
                          <Button variant="outline" size="sm">
                            Choose Files
                          </Button>
                        </div>
                      )}
                      
                      {/* Website URL Cases */}
                      {(companyAddressVerification === "business-website" ||
                        companyAddressVerification === "company-website-address" || 
                        companyAddressVerification === "linkedin-address") && (
                        <div className="space-y-1.5">
                          <Label htmlFor="verification-url" className="flex items-center gap-1">
                            {companyAddressVerification === "linkedin-address" 
                              ? "Company LinkedIn Page URL" 
                              : companyAddressVerification === "business-website"
                              ? "Business Website URL"
                              : "Company Website URL"}
                            <span className="text-foreground">*</span>
                          </Label>
                          <Input 
                            id="verification-url" 
                            type="url"
                            value={formData.businessWebsite}
                            onChange={(e) => updateFormData("businessWebsite", e.target.value)}
                            placeholder={
                              companyAddressVerification === "linkedin-address" 
                                ? "https://linkedin.com/company/yourcompany"
                                : companyAddressVerification === "business-website"
                                ? "https://company.com" 
                                : "https://company.com/contact-us"
                            }
                            className={cn(
                              "text-foreground",
                              businessValidationErrors.includes("verificationUrl") && "bg-red-50 border-red-300"
                            )}
                            required
                          />
                         </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Address Verification Important Notice */}
                <div className="bg-muted/50 rounded-lg p-2">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="h-3 w-3 text-destructive mt-0.5" />
                    <div className="text-xs">
                      <span className="font-medium text-destructive">IMPORTANT!</span> Verification documents must show the same name and address as listed on Open Supply Hub.
                    </div>
                  </div>
                </div>


                <div className="flex justify-between pt-2">
                  <Button variant="outline" onClick={() => setActiveTab("contact")}>
                    Back
                  </Button>
                  <Button 
                    onClick={() => {
                      if (validateBusinessFields()) {
                        markSectionComplete("business");
                        setActiveTab("facility");
                      }
                    }}
                    className={isBusinessValid() ? "bg-green-600 hover:bg-green-700" : ""}
                  >
                    Continue to Production Location Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="facility">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Open Supply Hub Profile
                </CardTitle>
                <CardDescription>
                  Detailed information about the production location (Optional)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <PremiumBetaBanner />
                <Accordion type="multiple" defaultValue={["overview", "company-hierarchy", "operations", "compliance", "environmental"]} className="w-full">
                  
                  {/* Section 1: Facility Overview */}
                  <AccordionItem value="overview" className="border rounded-lg px-4 mb-4">
                    <AccordionTrigger className="hover:no-underline py-4">
                      <div className="flex items-center gap-3 text-left">
                        <div className="p-2 bg-primary/10 rounded-md">
                          <Building2 className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold">Production Location Overview</h3>
                          <p className="text-sm text-muted-foreground">Basic facility identification and contact information</p>
                        </div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pt-4 pb-6 space-y-6">

                       <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Label htmlFor="local-language-name">Production Location Name in Native Language</Label>
                            <Tooltip>
                              <TooltipTrigger>
                                <HelpCircle className="h-4 w-4 text-muted-foreground" />
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Enter the production location name in the local language if different from the English name</p>
                              </TooltipContent>
                            </Tooltip>
                          </div>
                          <Input 
                            id="local-language-name" 
                            value={formData.localLanguageName}
                            onChange={(e) => updateFormData("localLanguageName", e.target.value)}
                            placeholder="Enter location name in native language (if different from English)" 
                          />
                        </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Label htmlFor="facility-phone" className="inline-flex items-center">
                              Company Phone
                              <PremiumBetaBadge />
                            </Label>
                            <Tooltip>
                              <TooltipTrigger>
                                <HelpCircle className="h-4 w-4 text-muted-foreground" />
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Main phone number for contacting this production location directly</p>
                              </TooltipContent>
                            </Tooltip>
                          </div>
                          <Input 
                            id="facility-phone" 
                            value={formData.facilityPhone}
                            onChange={(e) => updateFormData("facilityPhone", e.target.value)}
                            placeholder="+1 (555) 123-4567" 
                          />
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Label htmlFor="facility-website">Company Website</Label>
                            <Tooltip>
                              <TooltipTrigger>
                                <HelpCircle className="h-4 w-4 text-muted-foreground" />
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Official website URL for this specific production location (if available)</p>
                              </TooltipContent>
                            </Tooltip>
                          </div>
                          <Input 
                            id="facility-website" 
                            value={formData.facilityWebsite}
                            onChange={(e) => updateFormData("facilityWebsite", e.target.value)}
                            placeholder="https://company.com" 
                          />
                        </div>
                      </div>

                       <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Label htmlFor="description" className="inline-flex items-center">
                              Production Location Description
                              <PremiumBetaBadge />
                            </Label>
                            <Tooltip>
                              <TooltipTrigger>
                                <HelpCircle className="h-4 w-4 text-muted-foreground" />
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Provide a brief overview of what this production location manufactures and its main business activities</p>
                              </TooltipContent>
                            </Tooltip>
                          </div>
                          <Textarea 
                            id="description" 
                            value={formData.description}
                            onChange={(e) => updateFormData("description", e.target.value)}
                            placeholder="Brief description of what this production location produces or its main activities"
                            className="min-h-[100px]"
                          />
                        </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Section 2: Company Information */}
                  <AccordionItem value="company-hierarchy" className="border rounded-lg px-4 mb-4">
                    <AccordionTrigger className="hover:no-underline py-4">
                      <div className="flex items-center gap-3 text-left">
                        <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-md">
                          <Building2 className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold">Company Information</h3>
                          <p className="text-sm text-muted-foreground">Parent company and office information</p>
                        </div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pt-4 pb-6 space-y-6">
                      <div className="space-y-4">
                        <h4 className="font-medium text-base">Parent Company / Owner Information</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Label htmlFor="parent-company-name">Parent Company Name / Supplier Group</Label>
                              <Tooltip>
                                <TooltipTrigger>
                                  <HelpCircle className="h-4 w-4 text-muted-foreground" />
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>The name of the parent company or corporate group that owns this production location</p>
                                </TooltipContent>
                              </Tooltip>
                            </div>
                            <Input 
                              id="parent-company-name" 
                              value={formData.parentCompanyName}
                              onChange={(e) => updateFormData("parentCompanyName", e.target.value)}
                              placeholder="Parent company name" 
                            />
                          </div>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h4 className="font-medium text-base">Office Information <span className="text-muted-foreground">(if different from production location)</span></h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Label htmlFor="office-name">Office Name</Label>
                              <Tooltip>
                                <TooltipTrigger>
                                  <HelpCircle className="h-4 w-4 text-muted-foreground" />
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Name of the corporate office or headquarters</p>
                                </TooltipContent>
                              </Tooltip>
                            </div>
                            <Input 
                              id="office-name" 
                              value={formData.officeName}
                              onChange={(e) => updateFormData("officeName", e.target.value)}
                              placeholder="Office name" 
                            />
                          </div>
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Label htmlFor="office-address">Office Address</Label>
                              <Tooltip>
                                <TooltipTrigger>
                                  <HelpCircle className="h-4 w-4 text-muted-foreground" />
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Physical address of the office location</p>
                                </TooltipContent>
                              </Tooltip>
                            </div>
                            <Input 
                              id="office-address" 
                              value={formData.officeAddress}
                              onChange={(e) => updateFormData("officeAddress", e.target.value)}
                              placeholder="Office address" 
                            />
                          </div>
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Label htmlFor="office-country">Office Country</Label>
                              <Tooltip>
                                <TooltipTrigger>
                                  <HelpCircle className="h-4 w-4 text-muted-foreground" />
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Country where the office is located</p>
                                </TooltipContent>
                              </Tooltip>
                            </div>
                            <Input 
                              id="office-country" 
                              value={formData.officeCountry}
                              onChange={(e) => updateFormData("officeCountry", e.target.value)}
                              placeholder="Country" 
                            />
                          </div>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Section 3: Operations & Capabilities */}
                  <AccordionItem value="operations" className="border rounded-lg px-4 mb-4">
                    <AccordionTrigger className="hover:no-underline py-4">
                      <div className="flex items-center gap-3 text-left">
                        <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-md">
                          <Factory className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold">Operations & Capabilities</h3>
                          <p className="text-sm text-muted-foreground">Production and operations details for your location</p>
                        </div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pt-4 pb-6 space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <Label htmlFor="sector">Industry / Sectors</Label>
                          <MultiSelect
                            options={SECTOR_OPTIONS}
                            value={formData.sector}
                            onChange={(values) => updateFormData("sector", values)}
                            placeholder="Select sectors..."
                          />
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Label htmlFor="facility-types">Facility / Processing Types</Label>
                            <Tooltip>
                              <TooltipTrigger>
                                <HelpCircle className="h-4 w-4 text-muted-foreground" />
                              </TooltipTrigger>
                              <TooltipContent>
                                <p className="max-w-xs">Examples: Cut & Sew, Dyeing, Knitting, Weaving, Printing, Embroidery, Finishing, Assembly</p>
                              </TooltipContent>
                            </Tooltip>
                          </div>
                          <MultiSelect
                            options={PROCESSING_TYPE_OPTIONS}
                            value={formData.facilityTypes}
                            onChange={(values) => updateFormData("facilityTypes", values)}
                            placeholder="Select processing types..."
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <Label htmlFor="product-types">Product Types</Label>
                          <Tooltip>
                            <TooltipTrigger>
                              <HelpCircle className="h-4 w-4 text-muted-foreground" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p className="max-w-xs">Examples: T-shirts, Jeans, Dresses, Shirts, Jackets, Underwear, Sportswear, Children's clothing</p>
                            </TooltipContent>
                          </Tooltip>
                        </div>
                        <Input 
                          id="product-types" 
                          value={formData.productTypes}
                          onChange={(e) => updateFormData("productTypes", e.target.value)}
                          placeholder="e.g., T-shirts, Jeans, Dresses" 
                        />
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Label htmlFor="number-of-workers">Number of Workers</Label>
                            <Tooltip>
                              <TooltipTrigger>
                                <HelpCircle className="h-4 w-4 text-muted-foreground" />
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Total number of employees working at this production location</p>
                              </TooltipContent>
                            </Tooltip>
                          </div>
                          <Input 
                            id="number-of-workers" 
                            value={formData.numberOfWorkers}
                            onChange={(e) => updateFormData("numberOfWorkers", e.target.value)}
                            placeholder="e.g., 500" 
                          />
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Label htmlFor="female-workers">% of Female Workers</Label>
                            <Tooltip>
                              <TooltipTrigger>
                                <HelpCircle className="h-4 w-4 text-muted-foreground" />
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Percentage of female employees out of the total workforce at this location</p>
                              </TooltipContent>
                            </Tooltip>
                          </div>
                          <Input 
                            id="female-workers" 
                            value={formData.femaleWorkers}
                            onChange={(e) => updateFormData("femaleWorkers", e.target.value)}
                            placeholder="e.g., 45%" 
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Label htmlFor="minimum-order" className="inline-flex items-center">
                              Minimum Order Quantity
                              <PremiumBetaBadge />
                            </Label>
                            <Tooltip>
                              <TooltipTrigger>
                                <HelpCircle className="h-4 w-4 text-muted-foreground" />
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Smallest order quantity this production location will accept from customers</p>
                              </TooltipContent>
                            </Tooltip>
                          </div>
                          <Input 
                            id="minimum-order" 
                            value={formData.minimumOrderQuantity}
                            onChange={(e) => updateFormData("minimumOrderQuantity", e.target.value)}
                            placeholder="e.g., 1000 units" 
                          />
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Label htmlFor="average-lead-time" className="inline-flex items-center">
                              Average Lead Time
                              <PremiumBetaBadge />
                            </Label>
                            <Tooltip>
                              <TooltipTrigger>
                                <HelpCircle className="h-4 w-4 text-muted-foreground" />
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Typical time required from order confirmation to product delivery</p>
                              </TooltipContent>
                            </Tooltip>
                          </div>
                          <Input 
                            id="average-lead-time" 
                            value={formData.averageLeadTime}
                            onChange={(e) => updateFormData("averageLeadTime", e.target.value)}
                            placeholder="e.g., 30 days" 
                          />
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Section 4: Compliance & Partnerships */}
                  <AccordionItem value="compliance" className="border rounded-lg px-4 mb-4">
                    <AccordionTrigger className="hover:no-underline py-4">
                      <div className="flex items-center gap-3 text-left">
                        <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-md">
                          <Award className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold">Compliance & Partnerships</h3>
                          <p className="text-sm text-muted-foreground">Certifications, affiliations, and industry standards</p>
                        </div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pt-4 pb-6 space-y-6">
                       <div className="space-y-2">
                         <div className="flex items-center gap-2">
                           <Label htmlFor="affiliations" className="inline-flex items-center">
                             Affiliations
                             <PremiumBetaBadge />
                           </Label>
                           <Tooltip>
                             <TooltipTrigger>
                               <HelpCircle className="h-4 w-4 text-muted-foreground" />
                             </TooltipTrigger>
                             <TooltipContent>
                               <p>Organizations, parent companies, or partner entities your facility is formally connected to</p>
                             </TooltipContent>
                           </Tooltip>
                         </div>
                         <MultiSelect
                           options={AFFILIATIONS_OPTIONS}
                           value={formData.affiliations}
                           onChange={(values) => updateFormData("affiliations", values)}
                           placeholder="Select affiliations..."
                         />
                       </div>

                       <div className="space-y-2">
                         <Label htmlFor="certifications" className="inline-flex items-center">
                           Certifications / Standards / Regulations
                           <PremiumBetaBadge />
                         </Label>
                         <MultiSelect
                           options={CERTIFICATIONS_OPTIONS}
                           value={formData.certifications}
                           onChange={(values) => updateFormData("certifications", values)}
                           placeholder="Select certifications..."
                         />
                       </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Section 5: Environmental Data */}
                  <AccordionItem value="environmental" className="border rounded-lg px-4 mb-4">
                    <AccordionTrigger className="hover:no-underline py-4">
                      <div className="flex items-center gap-3 text-left">
                        <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-md">
                          <Leaf className="h-5 w-5 text-green-600 dark:text-green-400" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold">Environmental Data</h3>
                          <p className="text-sm text-muted-foreground">Emissions estimates and energy consumption data</p>
                        </div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pt-4 pb-6">
                      <div className="space-y-6 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-950/20 dark:to-blue-950/20 p-6 rounded-lg border border-green-200 dark:border-green-800">
                        <div className="space-y-2">
                          <h4 className="text-lg font-semibold text-foreground flex items-center gap-2">
                            <span className="text-green-600 dark:text-green-400">🌍</span>
                            Free Emissions Estimates
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            Fill in these fields, and Open Supply Hub—together with <strong>Climate TRACE</strong>—will provide a free emissions estimate for this location. This also helps your partners calculate emissions across their entire value chain.
                          </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Label htmlFor="opening-date">Opening Date</Label>
                              <Tooltip>
                                <TooltipTrigger>
                                  <HelpCircle className="h-4 w-4 text-muted-foreground" />
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Enter the date your production location officially started operations</p>
                                </TooltipContent>
                              </Tooltip>
                            </div>
                            <Popover>
                              <PopoverTrigger asChild>
                                <Button
                                  variant="outline"
                                  className={cn(
                                    "w-full justify-start text-left font-normal",
                                    !formData.openingDate && "text-muted-foreground"
                                  )}
                                >
                                  <CalendarIcon className="mr-2 h-4 w-4" />
                                  {formData.openingDate ? format(formData.openingDate, "yyyy") : <span>Select year</span>}
                                </Button>
                              </PopoverTrigger>
                              <PopoverContent className="w-auto p-0" align="start">
                                <Calendar
                                  mode="single"
                                  selected={formData.openingDate}
                                  onSelect={(date) => updateFormData("openingDate", date)}
                                  disabled={(date) => date > new Date()}
                                  initialFocus
                                  className={cn("p-3 pointer-events-auto")}
                                />
                              </PopoverContent>
                            </Popover>
                          </div>
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Label htmlFor="closing-date">Closing Date</Label>
                              <Tooltip>
                                <TooltipTrigger>
                                  <HelpCircle className="h-4 w-4 text-muted-foreground" />
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Enter the date your production location permanently stopped operating. Leave blank if still active.</p>
                                </TooltipContent>
                              </Tooltip>
                            </div>
                            <Popover>
                              <PopoverTrigger asChild>
                                <Button
                                  variant="outline"
                                  className={cn(
                                    "w-full justify-start text-left font-normal",
                                    !formData.closingDate && "text-muted-foreground"
                                  )}
                                >
                                  <CalendarIcon className="mr-2 h-4 w-4" />
                                  {formData.closingDate ? format(formData.closingDate, "MMM yyyy") : <span>Select month/year</span>}
                                </Button>
                              </PopoverTrigger>
                              <PopoverContent className="w-auto p-0" align="start">
                                <Calendar
                                  mode="single"
                                  selected={formData.closingDate}
                                  onSelect={(date) => updateFormData("closingDate", date)}
                                  disabled={(date) => date < new Date()}
                                  initialFocus
                                  className={cn("p-3 pointer-events-auto")}
                                />
                              </PopoverContent>
                            </Popover>
                          </div>
                        </div>

                        <div className="space-y-4">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Label htmlFor="throughput">Estimated Annual Throughput</Label>
                              <Tooltip>
                                <TooltipTrigger>
                                  <HelpCircle className="h-4 w-4 text-muted-foreground" />
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Total amount of materials or products processed by this location per year</p>
                                </TooltipContent>
                              </Tooltip>
                            </div>
                            <Input 
                              id="throughput" 
                              value={formData.throughput}
                              onChange={(e) => updateFormData("throughput", e.target.value)}
                              placeholder="e.g., 10,000 kg/year" 
                            />
                          </div>
                          
                          <div className="space-y-4">
                            <Label>Actual Annual Energy Consumption</Label>
                            <div className="space-y-3">
                              {[
                                { key: 'coal', label: 'Coal', unit: 'J' },
                                { key: 'naturalGas', label: 'Natural Gas', unit: 'J' },
                                { key: 'diesel', label: 'Diesel', unit: 'J' },
                                { key: 'kerosene', label: 'Kerosene', unit: 'J' },
                                { key: 'biomass', label: 'Biomass', unit: 'J' },
                                { key: 'charcoal', label: 'Charcoal', unit: 'J' },
                                { key: 'animalWaste', label: 'Animal Waste', unit: 'J' },
                                { key: 'electricity', label: 'Electricity', unit: 'MWh' },
                                { key: 'other', label: 'Other', unit: 'J' }
                              ].map((source) => (
                                <div key={source.key} className="flex items-center gap-3">
                                  <div className="flex items-center space-x-2">
                                    <input
                                      type="checkbox"
                                      id={`energy-${source.key}`}
                                      checked={formData.energyConsumption[source.key].selected}
                                      onChange={(e) => updateEnergyConsumption(source.key, 'selected', e.target.checked)}
                                      className="rounded border-gray-300"
                                    />
                                    <Label htmlFor={`energy-${source.key}`} className="min-w-[100px]">
                                      {source.label}:
                                    </Label>
                                  </div>
                                  <Input
                                    value={formData.energyConsumption[source.key].value}
                                    onChange={(e) => updateEnergyConsumption(source.key, 'value', e.target.value)}
                                    placeholder={`Enter value in ${source.unit}`}
                                    disabled={!formData.energyConsumption[source.key].selected}
                                    className="flex-1"
                                  />
                                  <span className="text-sm text-muted-foreground min-w-[40px]">
                                    {source.unit}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>

                <div className="flex justify-between pt-4">
                  <Button variant="outline" onClick={() => setActiveTab("business")}>
                    Back
                  </Button>
                  <Button 
                    onClick={() => {
                      markSectionComplete("facility");
                      // Handle form submission
                    }}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    Submit Claim
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
        </div>
        </main>

        {/* Footer */}
        <footer className="bg-gray-900 text-white mt-20">
          <div className="container mx-auto px-6 py-16">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
              <div className="space-y-6">
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-white rounded flex items-center justify-center">
                    <div className="grid grid-cols-2 gap-0.5">
                      <div className="w-1 h-1 bg-gray-900 rounded-sm"></div>
                      <div className="w-1 h-1 bg-gray-900 rounded-sm"></div>
                      <div className="w-1 h-1 bg-gray-900 rounded-sm"></div>
                      <div className="w-1 h-1 bg-gray-900 rounded-sm"></div>
                    </div>
                  </div>
                  <span className="font-bold text-white">OPEN SUPPLY HUB</span>
                </div>
                <p className="text-sm text-gray-300 leading-relaxed">
                  Open Supply Hub is established as a 501(c)(3) nonprofit organization, registered in the USA. 
                  This site was designed for low energy usage and is hosted on data centers using 100% renewable energy.
                </p>
              </div>
              
              <div className="space-y-4">
                <h4 className="font-semibold text-white">Resources</h4>
                <div className="space-y-3">
                  <a href="#" className="block text-sm text-gray-300 hover:text-white">Donate</a>
                  <a href="#" className="block text-sm text-gray-300 hover:text-white">FAQs</a>
                  <a href="#" className="block text-sm text-gray-300 hover:text-white">Media Hub</a>
                  <a href="#" className="block text-sm text-gray-300 hover:text-white">Terms of Service</a>
                  <a href="#" className="block text-sm text-gray-300 hover:text-white">Reporting Line</a>
                </div>
              </div>
              
              <div className="space-y-4">
                <h4 className="font-semibold text-white">Company</h4>
                <div className="space-y-3">
                  <a href="#" className="block text-sm text-gray-300 hover:text-white">Subscribe</a>
                  <a href="#" className="block text-sm text-gray-300 hover:text-white">Careers</a>
                  <a href="#" className="block text-sm text-gray-300 hover:text-white">Blog</a>
                  <a href="#" className="block text-sm text-gray-300 hover:text-white">Privacy Policy</a>
                  <a href="#" className="block text-sm text-gray-300 hover:text-white">Contact Us</a>
                </div>
              </div>
              
              <div className="space-y-4">
                <h4 className="font-semibold text-white">Follow Us</h4>
                <div className="flex space-x-4">
                  <Linkedin className="w-5 h-5 text-gray-300 hover:text-white cursor-pointer" />
                  <Github className="w-5 h-5 text-gray-300 hover:text-white cursor-pointer" />
                  <Twitter className="w-5 h-5 text-gray-300 hover:text-white cursor-pointer" />
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </TooltipProvider>
  );
};

export default ClaimsForm;
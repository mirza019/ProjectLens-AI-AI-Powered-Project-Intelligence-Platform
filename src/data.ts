import type { Project, Risk } from './types';

export const projects: Project[] = [
  {id:'aurora',name:'Project Aurora',code:'PL-2401',customer:'Northstar Utilities',region:'Europe',value:84000000,completion:68,margin:11.8,variance:900000,scheduleDays:21,riskExposure:3450000,status:'Critical'},
  {id:'orion',name:'Project Orion',code:'PL-2402',customer:'Vertex Infrastructure',region:'Middle East',value:128000000,completion:42,margin:16.4,variance:310000,scheduleDays:4,riskExposure:1920000,status:'Monitor'},
  {id:'atlas',name:'Project Atlas',code:'PL-2403',customer:'Apex Grid Partners',region:'Americas',value:56000000,completion:81,margin:18.7,variance:-420000,scheduleDays:0,riskExposure:640000,status:'Healthy'},
  {id:'nova',name:'Project Nova',code:'PL-2404',customer:'Meridian Engineering',region:'Asia Pacific',value:97000000,completion:55,margin:9.6,variance:1240000,scheduleDays:14,riskExposure:2810000,status:'Attention'},
  {id:'summit',name:'Project Summit',code:'PL-2405',customer:'Continental Works',region:'Europe',value:43000000,completion:73,margin:15.3,variance:180000,scheduleDays:3,riskExposure:780000,status:'Monitor'},
  {id:'harbor',name:'Project Harbor',code:'PL-2406',customer:'Bluewater Systems',region:'Americas',value:71000000,completion:36,margin:17.1,variance:-160000,scheduleDays:0,riskExposure:510000,status:'Healthy'},
];

export const risks: Risk[] = [
  {id:'R-108',projectId:'aurora',title:'Main transformer supplier delay',category:'Supplier',probability:.72,impact:3200000,exposure:2304000,owner:'Elena Rossi',status:'Open',mitigation:'Expedited logistics and weekly supplier recovery plan',reviewOverdue:true},
  {id:'R-207',projectId:'nova',title:'Engineering rework after interface change',category:'Engineering',probability:.55,impact:2600000,exposure:1430000,owner:'Jonas Weber',status:'Mitigating',mitigation:'Design freeze and joint interface review'},
  {id:'R-131',projectId:'orion',title:'Customer acceptance criteria ambiguity',category:'Contract',probability:.44,impact:2100000,exposure:924000,owner:'Priya Nair',status:'Open',mitigation:'Clarification submitted as formal notice'},
  {id:'R-305',projectId:'summit',title:'Commodity price escalation',category:'Commercial',probability:.38,impact:1800000,exposure:684000,owner:'Marc Dubois',status:'Monitoring',mitigation:'Hedge review and indexed supplier terms'}
];

export const forecastData = [
  {month:'Apr',budget:51.2,forecast:51.4,actual:31.2},{month:'May',budget:51.2,forecast:51.7,actual:34.8},{month:'Jun',budget:51.2,forecast:52.0,actual:38.1},{month:'Jul',budget:51.2,forecast:52.1,actual:41.7},{month:'Aug',budget:51.2,forecast:52.4,actual:44.6},{month:'Sep',budget:51.2,forecast:53.3,actual:47.2}
];

export const money = (v:number, compact=true) => new Intl.NumberFormat('en-GB',{style:'currency',currency:'EUR',notation:compact?'compact':'standard',maximumFractionDigits:1}).format(v);


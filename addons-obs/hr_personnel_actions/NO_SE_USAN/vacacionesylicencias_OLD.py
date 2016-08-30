"""
Esta era la forma en como estaba anteriormente programada las vacaciones y
lecencias.
Se remplazo con una funcion para simplificar el codigo y reutilizarlo.
"""


# # Abandono de Cargo
#                     if action.action_out_requested == '1':
#
#                         hr_cont_obj.write(cr, uid, contratos,
#                                           {'date_end':action.effective_date}
#                         )
#
#                         hr_obj.write(cr, uid, action.employee_id.id,
#                                      {'active': False},
#                                      context=None
#                         )
#                         self.write(cr, uid, action.id, {'states': 'applied',
#                                                         },
#                                    context=None
#                         )
#
#                     # Desahucio
#                     elif action.action_out_requested == '2':
#                         hr_cont_obj.write(cr, uid, contratos,
#                                           {'date_end':action.effective_date}
#                         )
#                         hr_obj.write(cr, uid, action.employee_id.id,
#                                      {'active': False}, context=None
#                         )
#                         self.write(cr, uid, action.id, {'states': 'applied',
#                                                         },
#                                    context=None
#                         )
#
#                     # Despido
#                     elif action.action_out_requested == '3':
#                         hr_cont_obj.write(cr, uid, contratos,
#                                           {'date_end':action.effective_date}
#                         )
#                         hr_obj.write(cr, uid, action.employee_id.id,
#                                      {'active': False}, context=None
#                         )
#                         self.write(cr, uid, action.id, {'states': 'applied',
#                                                         },
#                                    context=None
#                         )
#
#                     # DImision
#                     elif action.action_out_requested == '4':
#                         hr_cont_obj.write(cr, uid, contratos,
#                                           {'date_end':action.effective_date}
#                         )
#                         hr_obj.write(cr, uid, action.employee_id.id,
#                                      {'active': False}, context=None
#                         )
#                         self.write(cr, uid, action.id, {'states': 'applied',
#                                                         },
#                                    context=None
#                         )
#
#                     # Fallecimiento
#                     elif action.action_out_requested == '5':
#                         hr_cont_obj.write(cr, uid, contratos,
#                                           {'date_end':action.effective_date}
#                         )
#                         hr_obj.write(cr, uid, action.employee_id.id,
#                                      {'active': False}, context=None
#                         )
#                         self.write(cr, uid, action.id, {'states': 'applied',
#                                                         },
#                                    context=None
#                         )
#
#                     # Pensionado
#                     elif action.action_out_requested == '6':
#                         hr_cont_obj.write(cr, uid, contratos,
#                                           {'date_end':action.effective_date}
#                         )
#                         hr_obj.write(cr, uid, action.employee_id.id,
#                                      {'active': False}, context=None
#                         )
#                         self.write(cr, uid, action.id, {'states': 'applied',
#                                                         },
#                                    context=None
#                         )
#
#                     # Renuncia --- # 20
#                     elif action.action_out_requested == '7':
#                         hr_obj.write(cr, uid, action.employee_id.id,
#                                      {'active': False}, context=None
#                         )
#                         self.write(cr, uid, action.id, {'states': 'applied',
#                                                         },
#                                    context=None
#                         )
#
#                     # Rescision de Nombramiento
#                     elif action.action_out_requested == '8':
#                         hr_cont_obj.write(cr, uid, contratos,
#                                           {'date_end':action.effective_date}
#                         )
#                         hr_obj.write(cr, uid, action.employee_id.id,
#                                      {'active': False}, context=None
#                         )
#                         self.write(cr, uid, action.id, {'states': 'applied',
#                                                         },
#                                    context=None
#                         )
#
#                     # Finalizacion de Pasantia
#                     elif action.action_out_requested == '9':
#                         hr_cont_obj.write(cr, uid, contratos,
#                                           {'date_end':action.effective_date}
#                         )
#                         hr_obj.write(cr, uid, action.employee_id.id,
#                                      {'active': False}, context=None
#                         )
#                         self.write(cr, uid, action.id, {'states': 'applied',
#                                                         },
#                                    context=None
#                         )
#
#                     # Finalizacion de Voluntariado
#                     elif action.action_out_requested == '10':
#                         hr_cont_obj.write(cr, uid, contratos,
#                                           {'date_end':action.effective_date}
#                         )
#                         hr_obj.write(cr, uid, action.employee_id.id,
#                                      {'active': False}, context=None
#                         )
#                         self.write(cr, uid, action.id, {'states': 'applied',
#                                                         },
#                                    context=None
#                         )
#
#                     # Finalizacion de Entrenamiento
#                     elif action.action_out_requested == '11':
#                         hr_cont_obj.write(cr, uid, contratos,
#                                           {'date_end':action.effective_date}
#                         )
#                         hr_obj.write(cr, uid, action.employee_id.id,
#                                      {'active': False}, context=None
#                         )
#                         self.write(cr, uid, action.id, {'states': 'applied',
#                                                         },
#                                    context=None
#                         )
#                         hr_cont_obj.write(cr, uid, contratos,
#                                           {'date_end':action.effective_date}
#                         )






# Asueto
# if action.action_others_requested == '1':
#     # pdb.set_trace()
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#           WHERE employee_id IN ({0}) ORDER BY id \
#           DESC LIMIT 1".format(action.employee_id.id)
#     )
#     res = cr.fetchmany()
#     print res
#     # Si res esta vacio crea la licencia
#     # si no esta vacio y la fecha que tiene es menor a
#     # la fecha actual tambien hace la accion.
#     if res:
#         if self.verificar_fechas(cr,uid,ids,res[0][0],
#                                  datetime.datetime.now()):
#         # num_days = self.calc_number_of_days(cr,uid,ids,
#         #                         action.effective_date,
#         #                         action.end_of_leave, False
#         # )
#
#             peticion = hr_holiday.create(cr, uid,
#                  {'type':'add',
#                   'name':'Solicitud Asuelto',
#                   'holiday_status_id':19,
#                   'holiday_type':'employee',
#                   'employee_id':action.employee_id.id,
#                   'number_of_days_temp': action.days_of_vacations,
#                   }
#             )
#             hr_holiday.write(cr, uid, peticion,
#                              {'state':'validate'},
#                              context=None
#             )
#
#             hh_id_id = hr_holiday.create(cr, uid,
#                  {'state': 'validate',
#                   'holiday_status_id': 19,
#                   'employee_id': action.employee_id.id,
#                   'department_id':action.proposed_dependency.id,
#                   'holiday_type': 'employee',
#                   'date_from': action.effective_date,
#                   'date_to': action.end_of_leave,
#                   'number_of_days_temp':action.days_of_vacations,
#                   'name':'Solicitud de Asuelto',
#                   }
#             )
#             hr_holiday.write(cr, uid, hh_id_id,
#                              {'state':'validate'},
#                              context=None
#             )
#
#             self.write(cr, uid, action.id,
#                        {'states':'applied'},
#                        context=None
#             )
#             # hr_obj.write(cr, uid, action.employee_id.id,
#             #              {'on_licence': True}, context=None
#             # )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         raise osv.except_osv('Error',
#                  'Este empleado cuenta \
#                  con vacaciones y/o asignadas!')
#
#
# # Licencia por alumbramiento Conyuge
# elif action.action_others_requested == '2':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays\
#         WHERE employee_id IN ({0}) ORDER BY id \
#         DESC LIMIT 1".format(action.employee_id.id)
#     )
#     res = cr.fetchmany()
#     print res
#     if len(res) == 0 or res[0][0] == None:
#
#         # hr_obj.write(cr, uid, action.employee_id.id,
#         #              {'on_licence': True}, context=None
#         # )
#         num_days = self.calc_number_of_days(cr,uid,ids,
#                                     action.effective_date,
#                                     action.end_of_leave)
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Solic. Alumbramiento de Conyuge',
#               'holiday_status_id':9,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': num_days,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#
#         hh_id = hr_holiday.create(cr, uid,
#              {'state': 'validate',
#               'holiday_status_id': 9,
#               'employee_id': action.employee_id.id,
#               'department_id': action.proposed_dependency.id,
#               'holiday_type': 'employee',
#               'date_from': action.effective_date,
#               'date_to': action.end_of_leave,
#               'number_of_days_temp': num_days,
#               'name':'Solicitud de Alumbramiento Conyuge',
#               },context=None
#         )
#         hr_holiday.write(cr, uid, hh_id_id,
#                          {'state':'validate'},
#                          context=None)
#         self.write(cr, uid, action.id, {'states':'applied',
#                                         },
#                    context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         raise osv.except_osv(_('Error'),
#                              _('Este empleado cuenta '
#                                'con vacaciones '
#                                'y/o Licencias asignadas!')
#                              )
#
# # Licencia por Enfermedad
# elif action.action_others_requested == '3':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#           WHERE employee_id IN ({0}) ORDER BY id \
#           DESC LIMIT 1".format(action.employee_id.id)
#     )
#     res = cr.fetchmany()
#     print res
#     if len(res) == 0:
#         # hr_obj.write(cr, uid, action.employee_id.id,
#         #              {'on_licence': True}, context=None
#         # )
#         num_days = self.calc_number_of_days(cr,uid,ids,
#                                   action.effective_date,
#                                   action.end_of_leave
#                             )
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Solic. Licencia por Enfermedad',
#               'holiday_status_id':6,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': num_days,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#         hh_id = hr_holiday.create(cr, uid,
#              {'state': 'validate',
#               'holiday_status_id': 6,
#               'employee_id': action.employee_id.id,
#               'department_id': action.proposed_dependency.id,
#               'holiday_type': 'employee',
#               'date_from': action.effective_date,
#               'date_to': action.end_of_leave,
#               'number_of_days_temp': num_days,
#               'name':'Solicitud de Licencia por Enfermedad',
#               },context=None
#         )
#         hr_holiday.write(cr, uid, {'state':'validate'},
#                          context=None
#         )
#         self.write(cr, uid, action.id, {'states':'applied',
#                                         },
#                    context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         raise osv.except_osv('Error',
#                 'Este empleado cuenta \
#                 con vacaciones y/o Licencias asignadas!')
#
# # Licencia por Fallecimiento de Familiar (Directo)
# elif action.action_others_requested == '4':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#           WHERE employee_id IN ({0}) ORDER BY id \
#          DESC LIMIT 1".format(action.employee_id.id)
#     )
#     num_days = self.calc_number_of_days(cr, uid, ids,
#                                     action.effective_date,
#                                     action.end_of_leave
#                                 )
#     res = cr.fetchmany()
#     print res
#     if len(res) == 0:
#         # hr_obj.write(cr, uid, action.employee_id.id,
#         #              {'on_licence': True}, context=None
#         # )
#
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Solic. Licencia Fallecimiento '
#                      'Familiar Direct.',
#               'holiday_status_id':7,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': num_days,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#
#         hh_id = hr_holiday.create(cr, uid,
#               {'state': 'validate',
#                 'holiday_status_id': 7,
#                 'employee_id': action.employee_id.id,
#                 'department_id': action.proposed_dependency.id,
#                 'holiday_type': 'employee',
#                 'date_from': action.effective_date,
#                 'date_to': action.end_of_leave,
#                 'number_of_days_temp': num_days,
#                'name':'Solicitud de Licencia '
#                       'Fallecimiento Familiar Directo',},
#                           context=None
#         )
#         hr_holiday.write(cr, uid, {'state':'validate'},
#                          context=None)
#         self.write(cr, uid, action.id, {'states':'applied',
#                                         },
#                    context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         raise osv.except_osv('Error',
#                     'Este empleado cuenta con licencias \
#                     y/o vacaciones asignadas!')
#
# # Licencia por Fallecimiento de Familiar (Indirecto)
# elif action.action_others_requested == '5':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#           WHERE employee_id IN ({0}) ORDER BY id \
#           DESC LIMIT 1".format(action.employee_id.id)
#     )
#     num_days = self.calc_number_of_days(cr, uid, ids,
#                                     action.effective_date,
#                                     action.end_of_leave)
#     res = cr.fetchmany()
#     print res
#     if len(res) == 0:
#         # hr_obj.write(cr, uid, action.employee_id.id,
#         #              {'on_licence': True}, context=None
#         # )
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Solic. Licencia Fallecimiento '
#                      'Familiar (Indirecto)',
#               'holiday_status_id':15,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': num_days,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#         hr_holiday.create(cr, uid,
#           {'state': 'validate',
#            'holiday_status_id': 15,
#            'employee_id':action.employee_id.id,
#             'department_id': action.proposed_dependency.id,
#             'holiday_type': 'employee',
#             'date_from': action.effective_date,
#             'date_to': action.end_of_leave,
#             'number_of_days_temp': num_days,
#            'name':'Solicitud de Licencia Fallecimiento Familiar '
#                   '(Indirecto)',},
#               context=None
#         )
#         hr_holiday.write(cr, uid, {'state':'validate'},
#                          context=None)
#         self.write(cr, uid, action.id, {'states':'applied',
#                                         },
#                    context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         raise osv.except_osv('Error',
#                     'Este empleado cuenta con licencias \
#                     y/o vacaciones asignadas!')
#
# # Licencia por Maternidad
# elif action.action_others_requested == '6':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#         WHERE employee_id IN ({0}) ORDER BY id \
#         DESC LIMIT 1".format(action.employee_id.id)
#     )
#     num_days = self.calc_number_of_days(cr, uid, ids,
#                                     action.effective_date,
#                                     action.end_of_leave)
#     res = cr.fetchmany()
#     print res
#     if len(res) == 0:
#         # hr_obj.write(cr, uid, action.employee_id.id,
#         #              {'on_licence': True}, context=None
#         # )
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Solic. Licencia por Maternidad',
#               'holiday_status_id':5,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': num_days,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#         hr_holiday.create(cr, uid,
#               {'state': 'validate',
#                 'holiday_status_id': 5,
#                 'employee_id': action.employee_id.id,
#                 'department_id':action.proposed_dependency.id,
#                 'holiday_type': 'employee',
#                 'date_from': action.effective_date,
#                 'date_to': action.end_of_leave,
#                 'number_of_days_temp':num_days,
#                'name':'Solicitud de Licencia '
#                       'por Maternidad',
#                 },context=None
#         )
#         hr_holiday.write(cr, uid, {'state':'validate'},
#                          context=None)
#         self.write(cr, uid, action.id, {'states':'applied',
#                                         },
#                    context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         raise osv.except_osv('Error',
#                     'Este empleado cuenta con licencias \
#                     y/o vacaciones asignadas!')
#
# # Licencia por Matrimonio
# elif action.action_others_requested == '7':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#         WHERE employee_id IN ({0}) ORDER BY id \
#         DESC LIMIT 1".format(action.employee_id.id)
#     )
#     num_days = self.calc_number_of_days(cr, uid, ids,
#                                     action.effective_date,
#                                     action.end_of_leave)
#     res = cr.fetchmany()
#     print res
#     if len(res) == 0:
#         # hr_obj.write(cr, uid, action.employee_id.id,
#         #              {'on_licence': True},context=None
#         # )
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Solic. Licencia por Matrimonio',
#               'holiday_status_id':8,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': num_days,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#         hr_holiday.create(cr, uid,
#               {'state': 'validate',
#                 'holiday_status_id': 8,
#                 'employee_id': action.employee_id.id,
#                 'department_id': action.proposed_dependency.id,
#                 'holiday_type': 'employee',
#                 'date_from': action.effective_date,
#                 'date_to': action.end_of_leave,
#                 'number_of_days_temp':num_days,
#                'name':'Solicitud de Licencia '
#                       'por Matrimonio',},
#                   context=None
#         )
#
#         self.write(cr, uid, action.id, {'states':'applied',
#                                         },
#                    context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         raise osv.except_osv('Error',
#                  'Este empleado cuenta con licencias \
#                  y/o vacaciones asignadas!')
#
# # Licencia sin disfrute de sueldo
# elif action.action_others_requested == '8':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#         WHERE employee_id IN ({0}) ORDER BY id \
#         DESC LIMIT 1".format(action.employee_id.id)
#     )
#     num_days = self.calc_number_of_days(cr, uid, ids,
#                                     action.effective_date,
#                                     action.end_of_leave)
#     res = cr.fetchmany()
#     print res
#     if len(res) == 0:
#         # hr_obj.write(cr, uid, action.employee_id.id,
#         #              {'on_licence': True}, context=None
#         # )
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Solic. Licencia sin disfrute de '
#                      'sueldo',
#               'holiday_status_id':20,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': num_days,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#         hr_holiday.create(cr, uid,
#               {'state': 'validate',
#                 'holiday_status_id': 20,
#                 'employee_id': action.employee_id.id,
#                 'department_id': action.proposed_dependency.id,
#                 'holiday_type': 'employee',
#                 'date_from': action.effective_date,
#                 'date_to': action.end_of_leave,
#                 'number_of_days_temp': num_days,
#                'name':'Solicitud de Licencia '
#                       'sin Disfrute de Sueldo',},
#                 context=None
#         )
#         hr_holiday.write(cr, uid, {'state':'validate'},
#                          context=None)
#         self.write(cr, uid, action.id, {'states':'applied',
#                                         },context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         raise osv.except_osv('Error',
#                     'Este empleado cuenta \
#                 con licencias y/o vacaciones asignadas!')
#
# # Tardanza
# elif action.action_others_requested == '9':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#         WHERE employee_id IN ({0}) ORDER BY id \
#         DESC LIMIT 1".format(action.employee_id.id)
#     )
#     res = cr.fetchmany()
#     print res
#
#
#     if len(res) == 0:
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Tardanza',
#               'holiday_status_id':10,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': 0,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#         hh_id = hr_holiday.create(cr, uid,
#           {
#             'holiday_status_id': 10,
#             'employee_id': action.employee_id.id,
#             'department_id':action.proposed_dependency.id,
#             'holiday_type': 'employee',
#             'date_from': action.effective_date,
#             'date_to': action.effective_date,
#             'horas': action.proposed_hours,
#             'name':'Tardanza',
#             'state': 'validate',
#             },context=None
#         )
#         hr_holiday.write(cr,uid,hh_id, {'state':'validate'},
#                          context=None)
#         self.write(cr, uid,action.id,
#                    {'states':'applied',},
#                    context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         raise osv.except_osv('Error',
#                     'Este empleado cuenta con licencias \
#                     y/o vacaciones asignadas!')
#
# # Medio Dia de Cumpleaños
# elif action.action_others_requested == '10':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#         WHERE employee_id IN ({0}) ORDER BY id \
#         DESC LIMIT 1".format(action.employee_id.id)
#     )
#     num_days = self.calc_number_of_days(cr, uid, ids,
#                                     action.effective_date,
#                                     action.end_of_leave)
#     res = cr.fetchmany()
#     print res
#     if len(res) == 0:
#         # hr_obj.write(cr, uid, action.employee_id.id,
#         #              {'on_licence': True}, context=None
#         # )
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Solic. Medio Dia de Cumpleanos',
#               'holiday_status_id':18,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': num_days,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#         hr_holiday.create(cr, uid,
#             {'state': 'validate',
#             'holiday_status_id': 18,
#             'employee_id': action.employee_id.id,
#             'department_id': action.proposed_dependency.id,
#             'holiday_type': 'employee',
#             'date_from': action.effective_date,
#             'date_to': action.end_of_leave,
#             'number_of_days_temp': num_days,
#             'name':'Solicitud de Medio Dia de Cumpleanos',
#              },context=None
#         )
#         hr_holiday.write(cr,uid,{'state':'validate'},
#                          context=None)
#         self.write(cr, uid, action.id, {'states':'applied',
#                                         },
#                    context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         raise osv.except_osv('Error',
#                     'Este empleado cuenta con licencias \
#                     y/o vacaciones asignadas!')
#
# # Vacaciones
# elif action.action_others_requested == '11':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#         WHERE employee_id IN ({0}) ORDER BY id \
#         DESC LIMIT 1".format(action.employee_id.id)
#     )
#     num_days = self.calc_number_of_days(cr, uid, ids,
#                                     action.effective_date,
#                                     action.end_of_leave)
#     res = cr.fetchmany()
#     print res
#     if len(res) == 0:
#         # hr_obj.write(cr, uid, action.employee_id.id,
#         #              {'on_vacation': True}, context=None
#         # )
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Solic. de Vacaciones',
#               'holiday_status_id':33,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': num_days,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#         hr_holiday.create(cr, uid,
#               {'state': 'validate',
#             'holiday_status_id': 33,
#             'employee_id': action.employee_id.id,
#             'department_id': action.proposed_dependency.id,
#             'holiday_type': 'employee',
#             'date_from': action.effective_date,
#             'date_to': action.end_of_leave,
#             'number_of_days_temp': num_days,
#            'name':'Solicitud de Vacaciones',},context=None
#         )
#         hr_holiday.write(cr, uid, {'state':'validate'},
#                          context=None)
#         self.write(cr, uid, action.id, {'states':'applied',
#                                         },
#                    context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         cr.commit()
#
#         raise osv.except_osv('Error',
#                  'Este empleado cuenta con licencias \
#                  y/o vacaciones asignadas!')
#
# # Permiso
# elif action.action_others_requested == '12':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#         WHERE employee_id IN ({0}) ORDER BY id \
#         DESC LIMIT 1".format(action.employee_id.id)
#     )
#     num_days = self.calc_number_of_days(cr, uid, ids,
#                                     action.effective_date,
#                                     action.end_of_leave)
#     res = cr.fetchmany()
#     print res
#     if len(res) == 0:
#         # hr_obj.write(cr, uid, action.employee_id.id,
#         #              {'on_licence': True}, context=None
#         # )
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Solic. de Permiso',
#               'holiday_status_id': 18,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': num_days,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#         hr_holiday.create(cr, uid,
#             {'state': 'validate',
#             'holiday_status_id': 18,
#             'employee_id': action.employee_id.id,
#             'department_id': action.proposed_dependency.id,
#             'holiday_type': 'employee',
#             'date_from': action.effective_date,
#             'date_to': action.end_of_leave,
#             'number_of_days_temp': num_days,
#             'name':'Solicitud de Permiso.',
#              },context=None
#         )
#         hr_holiday.write(cr, uid, {'state':'validate'},
#                          context=None)
#         self.write(cr, uid, action.id, {'states':'applied',
#                                         },
#                    context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         raise osv.except_osv('Error',
#                     'Este empleado cuenta con licencias \
#                     y/o vacaciones asignadas!')
#
# # Licencia por Estudios
# elif action.action_others_requested == '13':
#     cr.execute(
#         "SELECT date_to FROM hr_holidays \
#         WHERE employee_id IN ({0}) ORDER BY id \
#         DESC LIMIT 1".format(action.employee_id.id)
#     )
#     num_days = self.calc_number_of_days(cr, uid, ids,
#                                     action.effective_date,
#                                     action.end_of_leave)
#     res = cr.fetchmany()
#     print res
#     if len(res) == 0:
#         # hr_obj.write(cr, uid, action.employee_id.id,
#         #              {'on_licence': True}, context=None
#         # )
#         peticion = hr_holiday.create(cr, uid,
#              {'type':'add',
#               'name':'Solic. Licencia por Estudios',
#               'holiday_status_id':14,
#               'holiday_type':'employee',
#               'employee_id':action.employee_id.id,
#               'number_of_days_temp': num_days,
#               }
#         )
#         hr_holiday.write(cr, uid, peticion,
#                          {'state':'validate'},
#                          context=None
#         )
#         hr_holiday.create(cr, uid,
#               {'state': 'validate',
#             'holiday_status_id': 14,
#             'employee_id': action.employee_id.id,
#             'department_id': action.proposed_dependency.id,
#             'holiday_type': 'employee',
#             'date_from': action.effective_date,
#             'date_to': action.end_of_leave,
#             'number_of_days_temp': num_days,
#            'name':'Solicitud de Licencia por Estudios',
#                },context=None
#         )
#         hr_holiday.write(cr,uid,{'state':'validate'},
#                          context=None)
#         self.write(cr, uid, action.id,
#                    {'states':'applied',
#                     },
#                    context=None
#         )
#     else:
#         self.write(cr, uid, ids, {'states': 'cancelled'},
#                    context=None
#         )
#         # cr.commit()
#
#         raise osv.except_osv('Error',
#                  'Este empleado cuenta con licencias \
#                  y/o vacaciones asignadas!')